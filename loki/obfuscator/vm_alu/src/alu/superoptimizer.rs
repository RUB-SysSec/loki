use crate::config::CONFIG;
use intermediate_language::il::assignment::Assignment;
use intermediate_language::il::linearized_expressions::{LinearExpr, LinearizedExpr};
use intermediate_language::{FastHashMap, FastHashSet};
use rand::prelude::*;
use rand::thread_rng;
use rayon::prelude::*;

pub struct SuperOptimizer {}

fn replace_expr_var(
    expr: &LinearizedExpr,
    cur_var: &LinearizedExpr,
    cur_rhs: &LinearizedExpr,
) -> LinearizedExpr {
    if cur_rhs.is_memory_op() {
        return expr.clone();
    }

    let positions: Vec<usize> = expr
        .0
        .iter()
        .enumerate()
        .filter(|(_, e)| e.is_var() && e == &cur_var.0.last().unwrap())
        .map(|(i, _)| i)
        .collect();

    let mut v: Vec<LinearExpr> = vec![];
    let mut last_pos = 0;

    for pos in positions {
        v.extend_from_slice(&expr.0[last_pos..pos]);

        v.extend_from_slice(&cur_rhs.0[0..]);
        last_pos = pos + 1;
    }

    if last_pos < expr.0.len() {
        v.extend_from_slice(&expr.0[last_pos..]);
    }

    LinearizedExpr::new(v)
}

fn check_expr_constraints(expr: &LinearizedExpr, max_depth: usize) -> bool {
    expr.num_unique_vars() <= 2
        && expr.num_unique_constants() <= 1
        && expr.0.len() >= CONFIG.min_superhandler_depth
        && expr.0.len() <= max_depth
}

//fn get_valid_sub_expr(expr: &LinearizedExpr) -> (usize, usize, LinearizedExpr) {
//    loop {
//        let (start, end, sub_expr) = rand_sub_expr(expr);
//        if check_expr_constraints(&sub_expr) {
//            break (start, end, sub_expr);
//        }
//    }
//}

impl SuperOptimizer {
    pub fn run(assignments: Vec<Assignment>) -> Vec<Assignment> {
        let ret = SuperOptimizer::superoptimize_assignments(assignments);

        ret
    }

    fn superoptimize_assignments(assignments: Vec<Assignment>) -> Vec<Assignment> {
        let map = SuperOptimizer::gen_ssa_map(&assignments);

        SuperOptimizer::eliminate_dead_code(
            assignments
                .into_par_iter()
                .map(|assignment| {
                    Assignment::new(
                        assignment.lhs,
                        SuperOptimizer::superoptimize_expression(assignment.rhs, &map),
                    )
                })
                .collect(),
        )
    }

    fn superoptimize_expression(
        expr: LinearizedExpr,
        map: &FastHashMap<LinearizedExpr, LinearizedExpr>,
    ) -> LinearizedExpr {
        if expr.is_memory_op() {
            return expr;
        }

        let mut current = expr;
        let mut before = current.clone();
        let max_depth: usize = thread_rng().gen_range(
            CONFIG.min_superhandler_depth,
            CONFIG.max_superhandler_depth + 1,
        );

        for _ in 0..100 {
            current = SuperOptimizer::derive_random_depth(&current, map);
            current = match check_expr_constraints(&current, max_depth) {
                true => current,
                false => before,
            };
            before = current.clone()
        }
        current
    }

    fn derive_random_depth(
        expr: &LinearizedExpr,
        map: &FastHashMap<LinearizedExpr, LinearizedExpr>,
    ) -> LinearizedExpr {
        let mut expr = expr.clone();
        for _ in 0..thread_rng().gen::<usize>() % 5 {
            expr = SuperOptimizer::derive_random_variable(expr, map);
        }
        expr
    }

    fn derive_random_variable(
        mut expr: LinearizedExpr,
        map: &FastHashMap<LinearizedExpr, LinearizedExpr>,
    ) -> LinearizedExpr {
        let vars = expr.get_vars();
        let v = vars.choose(&mut thread_rng());

        if v.is_some() {
            expr = match map.get(&v.unwrap()) {
                Some(replacement) => replace_expr_var(&expr, &v.unwrap(), replacement),
                None => expr,
            };
        }

        expr
    }

    fn gen_ssa_map(assignments: &Vec<Assignment>) -> FastHashMap<LinearizedExpr, LinearizedExpr> {
        assignments
            .into_par_iter()
            .map(|a| (a.lhs.clone(), a.rhs.clone()))
            .collect()
    }

    fn eliminate_dead_code(assignments: Vec<Assignment>) -> Vec<Assignment> {
        // return assignments;
        let used_vars = SuperOptimizer::find_used(&assignments);
        assignments
            .into_par_iter()
            .filter(|a| used_vars.contains(&a.lhs))
            .collect()
    }

    fn find_used(assignments: &Vec<Assignment>) -> FastHashSet<LinearizedExpr> {
        let mut ret = FastHashSet::default();
        let map = SuperOptimizer::gen_ssa_map(&assignments);
        let mut worklist = vec![assignments.last().unwrap().lhs.clone()];

        assignments
            .iter()
            .filter(|a| a.rhs.is_memory_op())
            .for_each(|a| worklist.push(a.lhs.clone()));

        while !worklist.is_empty() {
            let cur_var: LinearizedExpr = worklist.pop().unwrap();

            if ret.contains(&cur_var) {
                continue;
            }

            let rhs = map.get(&cur_var).expect("No entry found");
            ret.insert(cur_var);

            for v in rhs.get_vars() {
                if map.contains_key(&v) {
                    worklist.push(v);
                }
            }
        }
        ret
    }
}
