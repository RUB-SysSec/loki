use il::expression_evaluator::ExprEvaluator;
use il::expression_utils::{concat, constant};
use il::linearized_expressions::*;
use std::ops::{BitAnd, BitOr, BitXor, Not};
use symbolic_execution::symbolic_simplifications::*;
use symbolic_execution::symbolic_state::SymbolicState;
use utils::bit_vecs::*;

pub struct SymbolicEvaluator {
    pub symbolic_state: SymbolicState,
    symbols: Vec<LinearExpr>,
}

impl SymbolicEvaluator {
    pub fn new(symbols: Vec<LinearExpr>) -> SymbolicEvaluator {
        SymbolicEvaluator {
            symbols: symbols.clone(),
            symbolic_state: SymbolicState::new(symbols),
        }
    }

    pub fn evaluate(&self, expr: &LinearizedExpr) -> LinearizedExpr {
        <dyn ExprEvaluator<LinearizedExpr>>::eval(&self.symbolic_state, expr)
    }

    pub fn reset(&mut self) {
        self.symbolic_state = SymbolicState::new(self.symbols.clone())
    }
}

impl ExprEvaluator<LinearizedExpr> for SymbolicState {
    fn eval_op_0(&self, expr: &LinearExpr) -> LinearizedExpr {
        //                println!("op: {:?}", expr);

        match expr.op {
            LinearExprOp::Const(_) => LinearizedExpr::from_linear_expr(expr.clone()),
            LinearExprOp::Reg(_) => self
                .replace_argument(&LinearizedExpr::from_linear_expr(expr.clone()))
                .clone(),

            LinearExprOp::RegSlice(..) => LinearizedExpr::from_linear_expr(expr.clone()),
            LinearExprOp::ConstSlice(..) => LinearizedExpr::from_linear_expr(expr.clone()),
            _ => {
                println!("expression operator {:?} not supported", expr.op);
                unreachable!();
            }
        }
    }

    fn eval_op_1(&self, x: &LinearizedExpr, expr: &LinearExpr) -> LinearizedExpr {
        match expr.op {
            LinearExprOp::ZeroExtend
            | LinearExprOp::SignExtend
            | LinearExprOp::Slice(..)
            | LinearExprOp::Mem => {}
            _ => assert_eq!(x.size(), expr.size),
        }

        //                                                println!("x: {:?}, op: {:?}", x, expr);
        match expr.op {
            LinearExprOp::Mem => {
                // bytewise memory model -- breaks with symbolic computations
                let mut ret = self.replace_memory_argument(x).clone();
                for index in 1..(expr.size / 8) {
                    let address = (x.clone() + constant(index as u64, x.size())).simplify();
                    ret = concat(self.replace_memory_argument(&address).clone(), ret);
                }
                ret.simplify()

                // required for symbolic computations
                // match ret == x {
                //     false => ret.clone(),
                //     true => no_simplification_op_1(x, expr)
                // }
            }
            LinearExprOp::SignExtend => simplify_sign_extend(self.replace_argument(x), expr),
            LinearExprOp::ZeroExtend => simplify_zero_extend(self.replace_argument(x), expr),
            LinearExprOp::Slice(start, end) => {
                simplify_slice(self.replace_argument(x), expr, start, end)
            }
            LinearExprOp::Not => simplify_op_1(self.replace_argument(x), expr, |x: u64| x.not()),
            LinearExprOp::Neg => {
                simplify_op_1(self.replace_argument(x), expr, |x: u64| x.wrapping_neg())
            }

            _ => {
                println!("expression operator {:?} not supported", expr.op);
                unreachable!();
            }
        }
    }

    fn eval_op_2(
        &self,
        y: &LinearizedExpr,
        x: &LinearizedExpr,
        expr: &LinearExpr,
    ) -> LinearizedExpr {
        match expr.op {
            LinearExprOp::Concat => {}
            _ => {
                assert_eq!(x.size(), y.size());
                assert_eq!(x.size(), expr.size);
            }
        }
        //                                println!("x: {:?}, y: {:?}, op: {:?}", x, y, expr );
        match expr.op {
            LinearExprOp::Add => simplify_commutative_op_2(
                self.replace_argument(x),
                self.replace_argument(y),
                expr,
                |x: u64, y: u64| x.wrapping_add(y),
            ),
            LinearExprOp::Sub => simplify_op_2(
                self.replace_argument(x),
                self.replace_argument(y),
                expr,
                |x: u64, y: u64| x.wrapping_sub(y),
            ),
            LinearExprOp::Or => simplify_commutative_op_2(
                self.replace_argument(x),
                self.replace_argument(y),
                expr,
                |x: u64, y: u64| x.bitor(y),
            ),
            LinearExprOp::And => simplify_commutative_op_2(
                self.replace_argument(x),
                self.replace_argument(y),
                expr,
                |x: u64, y: u64| x.bitand(y),
            ),
            LinearExprOp::Xor => simplify_commutative_op_2(
                self.replace_argument(x),
                self.replace_argument(y),
                expr,
                |x: u64, y: u64| x.bitxor(y),
            ),
            LinearExprOp::Nand => simplify_commutative_op_2(
                self.replace_argument(x),
                self.replace_argument(y),
                expr,
                |x: u64, y: u64| !x.bitand(y),
            ),
            LinearExprOp::Nor => simplify_commutative_op_2(
                self.replace_argument(x),
                self.replace_argument(y),
                expr,
                |x: u64, y: u64| !x.bitor(y),
            ),
            LinearExprOp::Mul => simplify_commutative_op_2(
                self.replace_argument(x),
                self.replace_argument(y),
                expr,
                |x: u64, y: u64| x.wrapping_mul(y),
            ),
            LinearExprOp::Concat => {
                simplify_concat(self.replace_argument(x), self.replace_argument(y), expr)
            }
            LinearExprOp::Urem => simplify_op_2(
                self.replace_argument(x),
                self.replace_argument(y),
                expr,
                |x: u64, y: u64| x.checked_rem(y).unwrap_or(x),
            ),
            LinearExprOp::Srem => simplify_op_2(
                self.replace_argument(x),
                self.replace_argument(y),
                expr,
                |x: u64, y: u64| srem(x, y, expr.size as u64),
            ),
            LinearExprOp::Udiv => simplify_op_2(
                self.replace_argument(x),
                self.replace_argument(y),
                expr,
                |x: u64, y: u64| {
                    x.checked_div(y)
                        .unwrap_or(mask_to_size(0xffffffffffffffff, expr.size))
                },
            ),
            LinearExprOp::Sdiv => simplify_op_2(
                self.replace_argument(x),
                self.replace_argument(y),
                expr,
                |x: u64, y: u64| sdiv(x, y, expr.size as u64),
            ),
            LinearExprOp::Ult => simplify_op_2(
                self.replace_argument(x),
                self.replace_argument(y),
                expr,
                |x: u64, y: u64| if x < y { 1 } else { 0 },
            ),
            LinearExprOp::Slt => simplify_op_2(
                self.replace_argument(x),
                self.replace_argument(y),
                expr,
                |x: u64, y: u64| slt(x, y, expr.size as u64),
            ),
            LinearExprOp::Ule => simplify_op_2(
                self.replace_argument(x),
                self.replace_argument(y),
                expr,
                |x: u64, y: u64| if x <= y { 1 } else { 0 },
            ),
            LinearExprOp::Sle => simplify_op_2(
                self.replace_argument(x),
                self.replace_argument(y),
                expr,
                |x: u64, y: u64| sle(x, y, expr.size as u64),
            ),
            LinearExprOp::Equal => simplify_commutative_op_2(
                self.replace_argument(x),
                self.replace_argument(y),
                expr,
                |x: u64, y: u64| if x.eq(&y) { 1 } else { 0 },
            ),
            LinearExprOp::Ashr => simplify_op_2(
                self.replace_argument(x),
                self.replace_argument(y),
                expr,
                |x: u64, y: u64| ashr(x, y, expr.size as u64),
            ),
            LinearExprOp::Lshr => simplify_op_2(
                self.replace_argument(x),
                self.replace_argument(y),
                expr,
                |x: u64, y: u64| shr(x, y, expr.size as u64),
            ),
            LinearExprOp::Shl => simplify_op_2(
                self.replace_argument(x),
                self.replace_argument(y),
                expr,
                |x: u64, y: u64| shl(x, y, expr.size as u64),
            ),
            _ => {
                println!("expression operator {:?} not supported", expr.op);
                unreachable!();
            }
        }
    }

    fn eval_op_3(
        &self,
        z: &LinearizedExpr,
        y: &LinearizedExpr,
        x: &LinearizedExpr,
        expr: &LinearExpr,
    ) -> LinearizedExpr {
        match expr.op {
            LinearExprOp::Ite => {
                assert_eq!(y.size(), z.size());
                assert_eq!(z.size(), expr.size);
                simplify_cond(
                    self.replace_argument(x),
                    self.replace_argument(y),
                    self.replace_argument(z),
                    expr,
                )
            }
            _ => {
                println!("expression operator {:?} not supported", expr.op);
                unreachable!();
            }
        }
    }
}
