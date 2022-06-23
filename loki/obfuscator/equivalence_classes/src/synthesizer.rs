use crate::se_utils::symbolic_execute_with_inputs;
use crate::state::State;
use blake2::{Blake2b, Digest};
use intermediate_language::il::assignment::Assignment;
use intermediate_language::il::expression_utils::*;
use intermediate_language::il::linearized_expressions::LinearizedExpr;
use intermediate_language::{FastHashMap, FastHashSet};
use rand::thread_rng;
use rand::Rng;
use rayon::prelude::*;
use std::fs::File;
use std::io::Write;
use std::mem::swap;

pub struct EquivClassSynthesizer {
    pub equiv_classes: FastHashMap<String, FastHashSet<LinearizedExpr>>,
    inputs: Vec<Vec<Assignment>>,
    size: usize,
    selection_only: bool,
    pub verbose: bool,
}

impl EquivClassSynthesizer {
    pub fn new(num_inputs: usize, size: usize) -> EquivClassSynthesizer {
        EquivClassSynthesizer {
            equiv_classes: FastHashMap::default(),
            inputs: EquivClassSynthesizer::gen_rand_inputs(num_inputs, size),
            size,
            selection_only: false,
            verbose: false,
        }
    }

    pub fn init_with_selection(&mut self, expressions: &Vec<LinearizedExpr>) {
        self.handle_terminals(expressions.iter().cloned().collect::<FastHashSet<_>>());
        self.selection_only = true;
    }

    pub fn serialize_to_string(&self) -> String {
        serde_json::to_string(&self.equiv_classes).unwrap()
    }

    pub fn serialize_to_file(&self, file_name: &str) {
        let mut file = File::create(file_name).unwrap();
        file.write_all(self.serialize_to_string().as_bytes())
            .unwrap();
    }

    fn gen_rand_inputs(n: usize, size: usize) -> Vec<Vec<Assignment>> {
        let mut ret: Vec<Vec<Assignment>> = (0..n)
            .into_iter()
            .map(|_| {
                vec![
                    Assignment::new(
                        reg("p0", size),
                        constant(EquivClassSynthesizer::gen_val_of_rand_size(), size),
                    ),
                    Assignment::new(
                        reg("p1", size),
                        constant(EquivClassSynthesizer::gen_val_of_rand_size(), size),
                    ),
                    Assignment::new(
                        reg("p2", size),
                        constant(EquivClassSynthesizer::gen_val_of_rand_size(), size),
                    ),
                ]
            })
            .collect();

        ret.extend_from_slice(
            [
                0x0,
                0x1,
                0x2,
                0x80,
                0xff,
                0x8000,
                0xffff,
                0x8000_0000,
                0xffff_ffff,
                0x8000_0000_0000_0000,
                0xffff_ffff_ffff_ffff,
            ]
            .iter()
            .map(|v| {
                vec![
                    Assignment::new(reg("p0", size), constant(*v, size)),
                    Assignment::new(reg("p1", size), constant(*v, size)),
                    Assignment::new(reg("p2", size), constant(*v, size)),
                ]
            })
            .collect::<Vec<_>>()
            .as_slice(),
        );

        ret
    }

    fn gen_val_of_rand_size() -> u64 {
        let coin = thread_rng().gen::<usize>() % 5;
        match coin {
            0 => thread_rng().gen::<u8>() as u64,
            1 => thread_rng().gen::<u16>() as u64,
            2 => thread_rng().gen::<u32>() as u64,
            3 => thread_rng().gen::<u64>(),
            4 => EquivClassSynthesizer::gen_special_values(),
            _ => unreachable!(),
        }
    }

    fn gen_special_values() -> u64 {
        let coin = thread_rng().gen::<usize>() % 11;

        match coin {
            0 => 0x0,
            1 => 0x1,
            2 => 0x2,
            3 => 0x80,
            4 => 0xff,
            5 => 0x8000,
            6 => 0xffff,
            7 => 0x8000_0000,
            8 => 0xffff_ffff,
            9 => 0x8000_0000_0000_0000,
            10 => 0xffff_ffff_ffff_ffff,
            _ => unreachable!(),
        }
    }

    fn contain_vars(state: &State, name: &str) -> bool {
        state
            .expr
            .0
            .iter()
            .filter(|x| x.is_var())
            .any(|x| x.get_var_name() == name)
    }

    fn store_non_terminal(state: &State, current_iter: usize, max_depth: usize) -> bool {
        if !state.is_normalized() {
            return false;
        }

        let number_non_terminals = state
            .expr
            .0
            .iter()
            .filter(|x| x.is_var() && x.get_var_name() == "NT")
            .count();

        let contains_x = EquivClassSynthesizer::contain_vars(state, "p0");
        let contains_y = EquivClassSynthesizer::contain_vars(state, "p1");
        let contains_z = EquivClassSynthesizer::contain_vars(state, "p2");

        match (contains_x, contains_y, contains_z) {
            _ if number_non_terminals + current_iter >= max_depth => false,
            (false, true, _) => false,
            (false, _, true) => false,
            (true, false, true) => false,
            _ => true,
        }
    }

    fn partition_layer_state(
        state: &mut State,
        layer_index: usize,
        max_depth: usize,
        mut terminals: FastHashSet<LinearizedExpr>,
        mut non_terminals: Vec<State>,
    ) -> (FastHashSet<LinearizedExpr>, Vec<State>) {
        while state.remaining_moves() {
            let next_state = state.next_state();

            if next_state.is_terminal() {
                terminals.insert(next_state.expr.simplify());
            } else if EquivClassSynthesizer::store_non_terminal(&next_state, layer_index, max_depth)
            {
                non_terminals.push(next_state);
            }
        }
        (terminals, non_terminals)
    }

    fn merge_layer_states(
        layer_tuple1: (FastHashSet<LinearizedExpr>, Vec<State>),
        layer_tuple2: (FastHashSet<LinearizedExpr>, Vec<State>),
    ) -> (FastHashSet<LinearizedExpr>, Vec<State>) {
        (
            EquivClassSynthesizer::merge_terminals(layer_tuple1.0, layer_tuple2.0),
            EquivClassSynthesizer::merge_non_terminals(layer_tuple1.1, layer_tuple2.1),
        )
    }

    fn merge_terminals(
        mut terminals1: FastHashSet<LinearizedExpr>,
        mut terminals2: FastHashSet<LinearizedExpr>,
    ) -> FastHashSet<LinearizedExpr> {
        if terminals1.len() < terminals2.len() {
            swap(&mut terminals1, &mut terminals2);
        }

        for t in terminals2.into_iter() {
            terminals1.insert(t);
        }
        terminals1
    }

    fn merge_non_terminals(
        mut non_terminals1: Vec<State>,
        mut non_terminals2: Vec<State>,
    ) -> Vec<State> {
        if non_terminals1.len() < non_terminals2.len() {
            swap(&mut non_terminals1, &mut non_terminals2);
        }

        for nt in non_terminals2.into_iter() {
            non_terminals1.push(nt);
        }
        non_terminals1
    }

    fn partition_layer(
        &mut self,
        layer_states: &mut Vec<State>,
        layer_index: usize,
        max_depth: usize,
    ) -> (FastHashSet<LinearizedExpr>, Vec<State>) {
        layer_states
            .into_par_iter()
            .fold(
                || (FastHashSet::default(), vec![]),
                |(terminals, non_terminals), state| {
                    EquivClassSynthesizer::partition_layer_state(
                        state,
                        layer_index,
                        max_depth,
                        terminals,
                        non_terminals,
                    )
                },
            )
            .reduce(
                || (FastHashSet::default(), vec![]),
                EquivClassSynthesizer::merge_layer_states,
            )
    }

    pub fn synthesize(&mut self, max_depth: usize) {
        let mut layer_states = vec![State::new(self.size)];

        for layer_index in 0..max_depth {
            if self.verbose {
                println!("Current layer: {}", layer_index);
            }

            let (terminal_layer, next_layer) =
                self.partition_layer(&mut layer_states, layer_index, max_depth);

            if self.verbose {
                println!(
                    "{} terminals and {} non-terminals",
                    terminal_layer.len(),
                    next_layer.len()
                );
            }

            self.handle_terminals(terminal_layer);
            layer_states = next_layer;
        }
        assert!(layer_states.is_empty());
    }

    fn handle_terminals(&mut self, terminals: FastHashSet<LinearizedExpr>) {
        let equiv_classes: Vec<_> = match self.selection_only {
            true => terminals
                .par_iter()
                .map(|t| (t.clone(), self.determine_equiv_class(t)))
                .filter(|(_, equiv_class)| self.equiv_classes.contains_key(equiv_class))
                .collect(),
            false => terminals
                .par_iter()
                .map(|t| (t.clone(), self.determine_equiv_class(t)))
                .collect(),
        };

        for (terminal, equiv_class) in equiv_classes {
            if let Some(entry) = self.equiv_classes.get_mut(&equiv_class) {
                entry.insert(terminal);
                continue;
            }
            let mut equiv_expressions = FastHashSet::default();
            equiv_expressions.insert(terminal);
            self.equiv_classes.insert(equiv_class, equiv_expressions);
        }
    }

    pub fn determine_equiv_class(&self, expr: &LinearizedExpr) -> String {
        let s: String = self
            .inputs
            .par_iter()
            .map(|inputs| format!("{};", calc_output(expr, inputs)))
            .collect();
        format!("{:x}", Blake2b::digest(s.as_bytes()))
    }
}

fn calc_output(expr: &LinearizedExpr, inputs: &Vec<Assignment>) -> u64 {
    symbolic_execute_with_inputs(expr, inputs).get_constant_val()
}
