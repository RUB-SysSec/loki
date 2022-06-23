use il::linearized_expressions::*;
use FastHashMap;

#[derive(Serialize, Deserialize, Debug, Eq, PartialEq, Clone)]
pub struct SymbolicState {
    pub variables: FastHashMap<LinearizedExpr, LinearizedExpr>,
    pub memory: FastHashMap<LinearizedExpr, LinearizedExpr>,
}

impl SymbolicState {
    pub fn new(symbols: Vec<LinearExpr>) -> SymbolicState {
        let mut state = SymbolicState {
            variables: FastHashMap::default(),
            memory: FastHashMap::default(),
        };

        for symbol in symbols.iter() {
            state.variables.insert(
                LinearizedExpr::new(vec![symbol.clone()]),
                LinearizedExpr::new(vec![symbol.clone()]),
            );
        }

        state
    }

    pub fn reset(&mut self) {
        self.variables.clear();
        self.memory.clear();
    }

    pub fn update(&mut self, temporal_state: &SymbolicState) {
        for (lhs, rhs) in &temporal_state.memory {
            if let Some(entry) = self.memory.get_mut(&lhs) {
                *entry = rhs.clone();
                continue;
            }
            self.memory.insert(lhs.clone(), rhs.clone());
            assert_eq!(self.memory[lhs], temporal_state.memory[lhs]);
        }

        for (lhs, rhs) in &temporal_state.variables {
            //            println!("{} = {}", lhs.to_infix(), rhs.to_infix());
            //            assert_eq!(lhs.0.len(), 1);
            if let Some(entry) = self.variables.get_mut(&lhs) {
                *entry = rhs.clone();
                continue;
            }
            self.variables.insert(lhs.clone(), rhs.clone());
            assert_eq!(self.variables[lhs], temporal_state.variables[lhs]);
        }
    }

    pub fn replace_memory_argument<'e, 's: 'e>(
        &'s self,
        expr: &'e LinearizedExpr,
    ) -> &'e LinearizedExpr {
        match self.memory.get(&expr) {
            // assertion should never trigger in concolic scenarios, but always in symbolic ones
            Some(entry) => {
                assert!(!entry.is_memory_op());
                entry
            }
            _ => {
                assert!(false);
                expr
            }
        }
    }

    pub fn replace_argument<'e, 's: 'e>(&'s self, expr: &'e LinearizedExpr) -> &'e LinearizedExpr {
        match expr.0.last().unwrap().op {
            LinearExprOp::Reg(_) if expr.0.len() == 1 && !expr.is_non_terminal() => {
                &self.variables[expr]
            }
            _ => expr,
        }
    }

    pub fn get_var(&self, k: &LinearizedExpr) -> LinearizedExpr {
        let v = match k.0.last().unwrap().op {
            LinearExprOp::Reg(_) => self.variables.get(k),
            LinearExprOp::Mem => self.memory.get(&k.get_expression_slice(0, k.len() - 1)),
            _ => unreachable!("No variable or memory expression."),
        };

        v.expect(&format!("Variable {} not in map", k.to_string()))
            .clone()
    }

    pub fn set_var(&mut self, k: &LinearizedExpr, v: LinearizedExpr) {
        if let Some(entry) = self.variables.get_mut(k) {
            *entry = v;
            return;
        }
        self.variables.insert(k.clone(), v);
    }
}
