use il::linearized_expressions::*;

pub trait ExprEvaluator<S> {
    fn eval_op_0(&self, expr: &LinearExpr) -> S;
    fn eval_op_1(&self, x: &S, expr: &LinearExpr) -> S;
    fn eval_op_2(&self, x: &S, y: &S, expr: &LinearExpr) -> S;
    fn eval_op_3(&self, x: &S, y: &S, z: &S, expr: &LinearExpr) -> S;
}

impl<S> dyn ExprEvaluator<S>
where
    S: std::fmt::Debug,
{
    pub fn eval(&self, expr: &LinearizedExpr) -> S {
        let mut stack = vec![];
        for e in expr.0.iter() {
            let n = e.arity();
            match n {
                0 => {
                    let res = self.eval_op_0(e);
                    stack.push(res);
                }
                1 => {
                    let res = self.eval_op_1(&stack.pop().unwrap(), e);
                    stack.push(res);
                }
                2 => {
                    let res = self.eval_op_2(&stack.pop().unwrap(), &stack.pop().unwrap(), e);
                    stack.push(res);
                }
                3 => {
                    let res = self.eval_op_3(
                        &stack.pop().unwrap(),
                        &stack.pop().unwrap(),
                        &stack.pop().unwrap(),
                        e,
                    );
                    stack.push(res);
                }
                _ => unreachable!(),
            }
        }
        assert_eq!(stack.len(), 1);
        stack.pop().unwrap()
    }
}
