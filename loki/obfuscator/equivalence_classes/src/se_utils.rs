use intermediate_language::il::assignment::Assignment;
use intermediate_language::il::linearized_expressions::{LinearExpr, LinearExprOp, LinearizedExpr};
use intermediate_language::symbolic_execution::symbolic_evaluator::SymbolicEvaluator;
use intermediate_language::symbolic_execution::symbolic_state::SymbolicState;

fn gen_symbols(size: usize) -> Vec<LinearExpr> {
    vec![
        LinearExpr::new(LinearExprOp::Reg("p0".to_string()), size),
        LinearExpr::new(LinearExprOp::Reg("p1".to_string()), size),
        LinearExpr::new(LinearExprOp::Reg("p2".to_string()), size),
        LinearExpr::new(LinearExprOp::Reg("NT".to_string()), size),
    ]
}

pub fn symbolic_execute_with_inputs(
    expr: &LinearizedExpr,
    inputs: &Vec<Assignment>,
) -> LinearizedExpr {
    let mut evaluator = SymbolicEvaluator::new(gen_symbols(expr.size()));
    let mut symbolic_state = SymbolicState::new(gen_symbols(expr.size()));
    for assignment in inputs {
        *symbolic_state.variables.get_mut(&assignment.lhs).unwrap() = assignment.rhs.clone();
    }
    evaluator.symbolic_state = symbolic_state;
    evaluator.evaluate(expr)
}
