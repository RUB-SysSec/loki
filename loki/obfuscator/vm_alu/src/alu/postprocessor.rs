use intermediate_language::il::assignment::Assignment;
use intermediate_language::il::expression_utils::*;
use intermediate_language::il::linearized_expressions::{LinearExpr, LinearExprOp, LinearizedExpr};

pub struct ALUPostProcessor {}

impl ALUPostProcessor {
    fn rewrite(expr: LinearizedExpr) -> LinearizedExpr {
        let mut stack: Vec<LinearizedExpr> = vec![];
        for e in expr.0.into_iter() {
            let n = e.arity();
            let res = match n {
                0 => ALUPostProcessor::eval_op_0(e),
                1 => ALUPostProcessor::eval_op_1(stack.pop().unwrap(), e),
                2 => ALUPostProcessor::eval_op_2(stack.pop().unwrap(), stack.pop().unwrap(), e),
                3 => ALUPostProcessor::eval_op_3(
                    stack.pop().unwrap(),
                    stack.pop().unwrap(),
                    stack.pop().unwrap(),
                    e,
                ),
                _ => unreachable!(),
            };
            stack.push(res);
        }
        assert_eq!(stack.len(), 1);
        stack.pop().unwrap()
    }

    pub fn rewrite_assignment(assignment: Assignment) -> Assignment {
        Assignment::new(assignment.lhs, ALUPostProcessor::rewrite(assignment.rhs))
    }

    pub fn rewrite_expression(expr: LinearizedExpr) -> LinearizedExpr {
        ALUPostProcessor::rewrite(expr)
    }

    fn eval_op_0(expr: LinearExpr) -> LinearizedExpr {
        match expr.op {
            LinearExprOp::Reg(ref s) => reg(s, expr.size),
            LinearExprOp::Const(x) => constant(x, expr.size),
            LinearExprOp::Nop => nop(expr.size),
            _ => unreachable!("Operator {:?} not implemented.", expr.op),
        }
    }

    fn eval_op_1(x: LinearizedExpr, expr: LinearExpr) -> LinearizedExpr {
        // println!("x: {:?} -- op: {:?}", x, expr);
        match expr.op {
            LinearExprOp::Slice(..) | LinearExprOp::ZeroExtend | LinearExprOp::SignExtend => {}
            LinearExprOp::Load => {}
            _ => assert_eq!(x.size(), expr.size),
        }
        match expr.op {
            LinearExprOp::Not => not(x, expr.size),
            LinearExprOp::Neg => neg(x, expr.size),
            LinearExprOp::ZeroExtend => zero_extend(x.clone(), expr.size),
            LinearExprOp::SignExtend => unreachable!(),
            LinearExprOp::Load => load(x.clone(), expr.size),
            _ => unreachable!("Operator {:?} not implemented.", expr.op),
        }
    }

    fn eval_op_2(y: LinearizedExpr, x: LinearizedExpr, expr: LinearExpr) -> LinearizedExpr {
        // println!("x: {:?} -- op: {:?}", x, expr);
        assert_eq!(x.size(), y.size());
        assert_eq!(y.size(), expr.size);

        match expr.op {
            LinearExprOp::Add => add(x, y, expr.size),
            LinearExprOp::Sub => sub(x, y, expr.size),
            LinearExprOp::Mul => mul(x, y, expr.size),
            LinearExprOp::Udiv => udiv(x, y, expr.size),
            LinearExprOp::Sdiv => sdiv(x, y, expr.size),
            LinearExprOp::Urem => urem(x, y, expr.size),
            LinearExprOp::Srem => srem(x, y, expr.size),
            LinearExprOp::Shl => shl(x, y, expr.size),
            LinearExprOp::Lshr => lshr_plain(x, y, expr.size),
            LinearExprOp::Ashr => ashr_plain(x, y, expr.size),
            LinearExprOp::And => and(x, y, expr.size),
            LinearExprOp::Or => or(x, y, expr.size),
            LinearExprOp::Xor => xor(x, y, expr.size),
            LinearExprOp::Nand => not(and(x, y, expr.size), expr.size),
            LinearExprOp::Nor => not(or(x, y, expr.size), expr.size),
            LinearExprOp::Ult => ult(x, y, expr.size),
            LinearExprOp::Slt => slt(x, y, expr.size),
            LinearExprOp::Ule => ule(x, y, expr.size),
            LinearExprOp::Sle => sle(x, y, expr.size),
            LinearExprOp::Equal => equal(x, y, expr.size),
            LinearExprOp::Store => unimplemented!(),
            LinearExprOp::Concat => unreachable!(),
            _ => unreachable!("Operator {:?} not implemented.", expr.op),
        }
    }

    fn eval_op_3(
        z: LinearizedExpr,
        y: LinearizedExpr,
        x: LinearizedExpr,
        expr: LinearExpr,
    ) -> LinearizedExpr {
        assert_eq!(x.size(), y.size());
        assert_eq!(y.size(), z.size());
        assert_eq!(z.size(), expr.size);
        match expr.op {
            LinearExprOp::Ite => ite(x, y, z, expr.size),
            _ => unreachable!("Operator {:?} not implemented.", expr.op),
        }
    }
}
