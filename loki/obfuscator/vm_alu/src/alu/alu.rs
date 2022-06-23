use crate::alu::postprocessor::ALUPostProcessor;
use crate::alu::scheduler::ALUSemanticsMapEntry;
use crate::alu::semantics_builder::SemanticsBuilder;
use crate::alu::translator::LLVMTranslator;
use crate::bytecode::keys::ALUKeys;
use crate::config::CONFIG;
use crate::smt::thwart::thwart;
use crate::synthesis::mba::rewrite_to_equivalent_mba;
use crate::term_rewriting::term_rewriter::TermRewriter;
use intermediate_language::il::assignment::Assignment;
use intermediate_language::il::expression_utils::*;
use intermediate_language::il::linearized_expressions::*;
use intermediate_language::il::ssa::SSA;
use rand::prelude::*;
use rand::thread_rng;
use rmp_serde;
use std::fs::File;
use std::io::Write;

pub struct ALU {
    pub index: usize,
    pub keys: ALUKeys,
    pub assignment: Assignment,
    pub assignment_original: Assignment,
}

impl ALU {
    fn gen_instructions(n: usize) -> Vec<LinearizedExpr> {
        SemanticsBuilder::gen_semantics(n)
    }

    pub fn new(
        index: usize,
        /* semantics that actually matter */
        alive_semantics: Option<&Vec<ALUSemanticsMapEntry>>,
        term_rewriter: &TermRewriter,
    ) -> ALU {
        let mut keys = ALUKeys::new();
        let assignment = match index {
            // load or store
            1 => ALU::memory_dummy(&mut keys),
            _ => ALU::thwart_smt(&mut keys, alive_semantics, term_rewriter),
        };
        let assignment_original = assignment.clone();

        ALU {
            assignment,
            keys,
            index,
            assignment_original,
        }
    }

    fn memory_dummy(keys: &mut ALUKeys) -> Assignment {
        // key for load
        keys.push(0);
        // key for store
        keys.push(1);
        // key for alloc
        keys.push(2);
        Assignment::new(reg("r", 64), LinearizedExpr::no_op(64))
    }

    fn num_instructions(alive_semantics: &Option<&Vec<ALUSemanticsMapEntry>>) -> usize {
        let min_num_instr = match alive_semantics
            .iter()
            .flat_map(|l| l.iter())
            .map(|e| e.key_index)
            .max()
        {
            Some(v) if v >= CONFIG.min_semantics_per_alu => v,
            _ => CONFIG.min_semantics_per_alu,
        };
        assert!(
            min_num_instr < CONFIG.max_semantics_per_alu,
            "min number of instructions < num semantics per alu"
        );
        /* +1 to avoid index == length (0-indexed) */
        thread_rng().gen_range(min_num_instr + 1, CONFIG.max_semantics_per_alu + 1)
    }

    pub fn thwart_smt(
        keys: &mut ALUKeys,
        alive_semantics: Option<&Vec<ALUSemanticsMapEntry>>,
        term_rewriter: &TermRewriter,
    ) -> Assignment {
        let mut instructions: Vec<_> =
            ALU::gen_instructions(ALU::num_instructions(&alive_semantics));

        alive_semantics
            .iter()
            .flat_map(|l| l.iter())
            .for_each(|alu_map_entry| {
                *instructions
                    .get_mut(alu_map_entry.key_index)
                    .expect(&format!(
                        "Could not access key index {}",
                        &alu_map_entry.key_index
                    )) = alu_map_entry.expr.clone();
            });

        instructions = instructions
            .into_iter()
            .map(|e| ALUPostProcessor::rewrite_expression(e))
            .map(|e| rewrite_to_equivalent_mba(e, &term_rewriter))
            .collect();

        ALUPostProcessor::rewrite_assignment(Assignment::new(
            reg("r", 64),
            rewrite_to_equivalent_mba(
                thwart(instructions.as_slice(), keys, &term_rewriter),
                &term_rewriter,
            ),
        ))
    }

    pub fn to_string(&self) -> String {
        let mut ret = String::new();

        /* assignment */
        ret.push_str("Assignment before rewriting:\n");
        ret.push_str(&format!("{}\n", self.assignment.to_string()));
        ret.push_str("\n");

        /* assignment */
        ret.push_str("Assignment after rewriting:\n");
        ret.push_str(&format!(
            "{}\n",
            ALUPostProcessor::rewrite_assignment(self.assignment.clone()).to_string()
        ));
        ret.push_str("\n");

        /* instructions */
        ret.push_str("Instructions:\n");

        let preprocessed = ALUPostProcessor::rewrite_assignment(self.assignment.clone());
        let ssa = SSA::from_assignments(&vec![preprocessed]);
        let instructions_string: String =
            ssa.iter().map(|a| format!("{}\n", a.to_string())).collect();

        ret.push_str(&instructions_string);
        ret.push_str("\n");

        /* keys */
        ret.push_str("Keys:\n");

        for (index, key) in self.keys.iter().enumerate() {
            ret.push_str(&format!("{}: {:#018x}\n", index, key))
        }

        ret
    }

    pub fn to_debug_file(&self, workdir: &String) {
        if !CONFIG.debug_output {
            return;
        }
        let file_name = format!("{}/debug_files/alu{}_debug.txt", workdir, self.index);
        ALU::to_file(&file_name, &self.to_string());

        let file_name = format!(
            "{}/debug_files/alu{}_assignment_with_mba.bin",
            workdir, self.index
        );
        let content =
            rmp_serde::to_vec(&self.assignment).expect("Could not serialize original assignment");
        let mut file = File::create(&file_name).unwrap();
        file.write_all(&content)
            .expect(&format!("Could not write to {}", file_name));
    }

    pub fn to_llvm(&self, workdir: &String) {
        let preprocessed = self.assignment.clone();
        let ssa = SSA::from_assignments(&vec![preprocessed]);
        let translated = LLVMTranslator::from_alu(&ssa);

        let file_name = format!("{}/alus/alu{}.txt", workdir, self.index);
        ALU::to_file(&file_name, &translated);

        self.to_debug_file(workdir);
    }

    pub fn to_file(file_name: &String, content: &String) {
        let mut file = File::create(file_name).unwrap();
        write!(&mut file, "{}", content).unwrap();
    }

    pub fn verify(&self) -> bool {
        let preprocessed = ALUPostProcessor::rewrite_assignment(self.assignment.clone());
        let ssa = SSA::from_assignments(&vec![preprocessed]);

        return ssa.len() > 10;
    }
}
