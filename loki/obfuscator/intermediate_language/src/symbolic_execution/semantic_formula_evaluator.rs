use il::assignment::Assignment;
use il::expression_evaluator::ExprEvaluator;
use il::linearized_expressions::*;
use il::semantic_formula::SemanticFormula;
use symbolic_execution::symbolic_state::SymbolicState;

pub struct SemanticFormulaEvaluator {
    pub symbolic_state: SymbolicState,
    temporal_state: SymbolicState,
    symbols: Vec<LinearExpr>,
}

impl SemanticFormulaEvaluator {
    pub fn new(symbols: Vec<LinearExpr>) -> SemanticFormulaEvaluator {
        let symbols_backup = symbols.clone();
        let symbolic_state = SymbolicState::new(symbols);
        let temporal_state = SymbolicState::new(vec![]);
        SemanticFormulaEvaluator {
            symbolic_state,
            temporal_state,
            symbols: symbols_backup,
        }
    }

    pub fn get_symbols(&self) -> Vec<LinearExpr> {
        self.symbols.clone()
    }

    pub fn eval_assignment(&mut self, assignment: &Assignment) {
        assert!(self.temporal_state.variables.is_empty() && self.temporal_state.memory.is_empty());

        let evaluated_expr_rhs = self.eval_expression(&assignment.rhs);
        self.update_temporal_state(&assignment.lhs, &evaluated_expr_rhs);

        self.symbolic_state.update(&self.temporal_state);
        self.temporal_state.reset();
    }

    pub fn eval_instruction_formular(&mut self, instruction: &SemanticFormula) {
        assert!(self.temporal_state.variables.is_empty() && self.temporal_state.memory.is_empty());
        for assignment in instruction.0.iter() {
            if assignment.is_nop() {
                continue;
            }
            let evaluated_expr_rhs = self.eval_expression(&assignment.rhs);
            self.update_temporal_state(&assignment.lhs, &evaluated_expr_rhs);
            //            println!("{:?} := {:?}", assignment.lhs.to_infix(), evaluated_expr.to_infix());
        }
        self.symbolic_state.update(&self.temporal_state);
        self.temporal_state.reset();
    }

    fn update_temporal_state(&mut self, lhs: &LinearizedExpr, rhs: &LinearizedExpr) {
        let mapping = match lhs.0.last().unwrap().op {
            LinearExprOp::Mem => &mut self.temporal_state.memory,
            LinearExprOp::Reg(_) => &mut self.temporal_state.variables,
            // LinearExprOp::RegSlice(..) => &mut self.temporal_state.variables,
            // LinearExprOp::Slice(..) => &mut self.temporal_state.variables,
            LinearExprOp::Const(x) if x == 0 || x == 1 => &mut self.temporal_state.variables,
            _ => {
                println!(
                    "operator {:?} not supported (expression: {})",
                    lhs.0.last().unwrap().op,
                    lhs.to_infix()
                );
                unreachable!()
            }
        };
        let lhs = match lhs.op().op {
            LinearExprOp::Mem => lhs.get_expression_slice(0, lhs.len() - 1),
            _ => lhs.clone(),
        };
        *mapping.entry(lhs.clone()).or_insert(lhs.clone()) = rhs.clone();
    }

    pub fn eval_expression(&self, expr: &LinearizedExpr) -> LinearizedExpr {
        <dyn ExprEvaluator<LinearizedExpr>>::eval(&self.symbolic_state, expr)
    }

    pub fn reset(&mut self) {
        self.symbolic_state = SymbolicState::new(self.symbols.clone());
    }
}
