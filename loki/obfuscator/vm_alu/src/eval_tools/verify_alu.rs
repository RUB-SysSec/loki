use intermediate_language::il::ssa::SSA;
use intermediate_language::symbolic_execution::semantic_formula_evaluator::SemanticFormulaEvaluator;
use rmp_serde;

use intermediate_language::il::assignment::Assignment;
use intermediate_language::il::expression_utils::*;
use std::env;
use std::fs;

pub fn main() {
    let args: Vec<String> = env::args().collect();
    if args.len() < 2 {
        println!("[x] Syntax: <file path>");
        return;
    }

    let file_path = args.get(1).expect("No file path provided.");

    let content = fs::read(&file_path).expect(&format!("File {} not found!", &file_path));
    let assignment: Assignment = rmp_serde::from_read(content.as_slice())
        .expect(&format!("Could not deserialize file {}.", &file_path));

    let constraints = vec![
        Assignment::new(reg("x", 64), constant(0x1a943, 64)),
        Assignment::new(reg("y", 64), constant(0x41, 64)),
        Assignment::new(reg("c", 64), constant(0xffffffff, 64)),
        Assignment::new(reg("k", 64), constant(0x253f4db642e981ca, 64)),
    ];
    let symbols = constraints
        .iter()
        .flat_map(|ass| ass.lhs.gen_se_symbols())
        .collect();

    let mut symbolic_executor = SemanticFormulaEvaluator::new(symbols);

    /* contraint for concolic execution */
    for c in constraints {
        symbolic_executor.eval_assignment(&c);
    }

    symbolic_executor.eval_assignment(&assignment);

    let result = symbolic_executor.symbolic_state.get_var(&assignment.lhs);

    println!("result: {}", result.to_string());

    // let ssa = SSA::from_assignments(&vec![assignment]);
    // println!("ssa len: {}", ssa.len());
}
