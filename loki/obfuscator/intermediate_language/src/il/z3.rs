use il::linearized_expressions::{LinearExpr, LinearExprOp, LinearizedExpr};
use seer_z3 as z3;

pub struct TranslatorZ3<'ctx> {
    context: &'ctx z3::Context,
}

impl<'ctx> TranslatorZ3<'ctx> {
    pub fn new(context: &'ctx z3::Context) -> TranslatorZ3<'ctx> {
        TranslatorZ3 { context }
    }

    pub fn translate(&self, expr: &LinearizedExpr) -> z3::Ast<'ctx> {
        self.eval(expr)
    }

    fn eval(&self, expr: &LinearizedExpr) -> z3::Ast<'ctx> {
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

    fn eval_op_0(&self, expr: &LinearExpr) -> z3::Ast<'ctx> {
        match expr.op {
            LinearExprOp::Reg(ref s) => self.context.named_bitvector_const(s, expr.size as u32),
            LinearExprOp::Const(x) => z3::Ast::bv_from_u64(self.context, x, expr.size as u32),
            _ => unreachable!("Operator {:?} not implemented.", expr.op),
        }
    }

    fn eval_op_1(&self, x: &z3::Ast<'ctx>, expr: &LinearExpr) -> z3::Ast<'ctx> {
        match expr.op {
            LinearExprOp::Not => x.bvnot(),
            LinearExprOp::Neg => x.bvneg(),
            LinearExprOp::Slice(start, end) => x.extract(end as u32, start as u32),
            //            LinearExprOp::ZeroExtend(size) => x.zero_extend(size as u32),
            //            LinearExprOp::SignExtend(size) => x.sign_extend(size as u32),
            _ => unreachable!("Operator {:?} not implemented.", expr.op),
        }
    }

    fn eval_op_2(&self, y: &z3::Ast<'ctx>, x: &z3::Ast<'ctx>, expr: &LinearExpr) -> z3::Ast<'ctx> {
        match expr.op {
            LinearExprOp::Add => x.bvadd(y),
            LinearExprOp::Sub => x.bvsub(y),
            LinearExprOp::Mul => x.bvmul(y),
            LinearExprOp::Udiv => x.bvudiv(y),
            LinearExprOp::Sdiv => x.bvsdiv(y),
            LinearExprOp::Urem => x.bvurem(y),
            LinearExprOp::Srem => x.bvsrem(y),
            LinearExprOp::Shl => x.bvshl(y),
            LinearExprOp::Lshr => x.bvlshr(y),
            LinearExprOp::Ashr => x.bvashr(y),
            LinearExprOp::And => x.bvand(y),
            LinearExprOp::Or => x.bvor(y),
            LinearExprOp::Xor => x.bvxor(y),
            LinearExprOp::Nand => x.bvnand(y),
            LinearExprOp::Nor => x.bvnor(y),
            LinearExprOp::Ult => z3::Ast::ite(
                &x.bvult(y),
                &z3::Ast::bv_from_u64(self.context, 1, expr.size as u32),
                &z3::Ast::bv_from_u64(self.context, 0, expr.size as u32),
            ),
            LinearExprOp::Slt => z3::Ast::ite(
                &x.bvslt(y),
                &z3::Ast::bv_from_u64(self.context, 1, expr.size as u32),
                &z3::Ast::bv_from_u64(self.context, 0, expr.size as u32),
            ),
            LinearExprOp::Ule => z3::Ast::ite(
                &x.bvule(y),
                &z3::Ast::bv_from_u64(self.context, 1, expr.size as u32),
                &z3::Ast::bv_from_u64(self.context, 0, expr.size as u32),
            ),
            LinearExprOp::Sle => z3::Ast::ite(
                &x.bvsle(y),
                &z3::Ast::bv_from_u64(self.context, 1, expr.size as u32),
                &z3::Ast::bv_from_u64(self.context, 0, expr.size as u32),
            ),
            LinearExprOp::Concat => x.concat(y),
            LinearExprOp::Equal => z3::Ast::ite(
                &x._eq(y),
                &z3::Ast::bv_from_u64(self.context, 1, expr.size as u32),
                &z3::Ast::bv_from_u64(self.context, 0, expr.size as u32),
            ),
            _ => unreachable!("Operator {:?} not implemented.", expr.op),
        }
    }

    fn eval_op_3(
        &self,
        z: &z3::Ast<'ctx>,
        y: &z3::Ast<'ctx>,
        x: &z3::Ast<'ctx>,
        expr: &LinearExpr,
    ) -> z3::Ast<'ctx> {
        match expr.op {
            LinearExprOp::Ite => z3::Ast::ite(
                &z3::Ast::not(&x._eq(&z3::Ast::bv_from_u64(self.context, 0, expr.size as u32))),
                y,
                z,
            ),
            _ => unreachable!("Operator {:?} not implemented.", expr.op),
        }
    }
}

pub struct TranslatorZ3PythonString {}

impl TranslatorZ3PythonString {
    pub fn translate(expr: &LinearizedExpr) -> String {
        TranslatorZ3PythonString::eval(expr)
    }

    fn eval(expr: &LinearizedExpr) -> String {
        let mut stack = vec![];
        for e in expr.0.iter() {
            let n = e.arity();
            match n {
                0 => {
                    let res = TranslatorZ3PythonString::eval_op_0(e);
                    stack.push(res);
                }
                1 => {
                    let res = TranslatorZ3PythonString::eval_op_1(&stack.pop().unwrap(), e);
                    stack.push(res);
                }
                2 => {
                    let res = TranslatorZ3PythonString::eval_op_2(
                        &stack.pop().unwrap(),
                        &stack.pop().unwrap(),
                        e,
                    );
                    stack.push(res);
                }
                3 => {
                    let res = TranslatorZ3PythonString::eval_op_3(
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

    fn eval_op_0(expr: &LinearExpr) -> String {
        match expr.op {
            LinearExprOp::Reg(ref s) => format!("BitVec(\"{}\", {})", s, expr.size),
            LinearExprOp::Const(x) => format!("BitVecVal({}, {})", x, expr.size),
            _ => unreachable!("Operator {:?} not implemented.", expr.op),
        }
    }

    fn eval_op_1(x: &String, expr: &LinearExpr) -> String {
        match expr.op {
            LinearExprOp::Not => format!("(~{})", x),
            LinearExprOp::Neg => format!("(-{})", x),
            // LinearExprOp::Slice(start, end) => x.extract(end as u32, start as u32),
            //            LinearExprOp::ZeroExtend(size) => x.zero_extend(size as u32),
            //            LinearExprOp::SignExtend(size) => x.sign_extend(size as u32),
            _ => unreachable!("Operator {:?} not implemented.", expr.op),
        }
    }

    fn eval_op_2(y: &String, x: &String, expr: &LinearExpr) -> String {
        match expr.op {
            LinearExprOp::Add => format!("({} + {})", x, y),
            LinearExprOp::Sub => format!("({} - {})", x, y),
            LinearExprOp::Mul => format!("({} * {})", x, y),
            // LinearExprOp::Udiv => x.bvudiv(y),
            // LinearExprOp::Sdiv => x.bvsdiv(y),
            LinearExprOp::Urem => format!("URem({}, {})", x, y),
            // LinearExprOp::Srem => x.bvsrem(y),
            LinearExprOp::Shl => format!("({} << {})", x, y),
            LinearExprOp::Lshr => format!("LShR({}, {})", x, y),
            LinearExprOp::Ashr => format!("({} >> {})", x, y),
            LinearExprOp::And => format!("({} & {})", x, y),
            LinearExprOp::Or => format!("({} | {})", x, y),
            LinearExprOp::Xor => format!("({} ^ {})", x, y),
            // LinearExprOp::Nand => x.bvnand(y),
            // LinearExprOp::Nor => x.bvnor(y),
            // LinearExprOp::Ult => z3::Ast::ite(
            //     &x.bvult(y),
            //     &z3::Ast::bv_from_u64(self.context, 1, expr.size as u32),
            //     &z3::Ast::bv_from_u64(self.context, 0, expr.size as u32),
            // ),
            // LinearExprOp::Slt => z3::Ast::ite(
            //     &x.bvslt(y),
            //     &z3::Ast::bv_from_u64(self.context, 1, expr.size as u32),
            //     &z3::Ast::bv_from_u64(self.context, 0, expr.size as u32),
            // ),
            // LinearExprOp::Ule => z3::Ast::ite(
            //     &x.bvule(y),
            //     &z3::Ast::bv_from_u64(self.context, 1, expr.size as u32),
            //     &z3::Ast::bv_from_u64(self.context, 0, expr.size as u32),
            // ),
            // LinearExprOp::Sle => z3::Ast::ite(
            //     &x.bvsle(y),
            //     &z3::Ast::bv_from_u64(self.context, 1, expr.size as u32),
            //     &z3::Ast::bv_from_u64(self.context, 0, expr.size as u32),
            // ),
            // LinearExprOp::Concat => x.concat(y),
            // LinearExprOp::Equal => z3::Ast::ite(
            //     &x._eq(y),
            //     &z3::Ast::bv_from_u64(self.context, 1, expr.size as u32),
            //     &z3::Ast::bv_from_u64(self.context, 0, expr.size as u32),
            // ),
            _ => unreachable!("Operator {:?} not implemented.", expr.op),
        }
    }

    fn eval_op_3(z: &String, y: &String, x: &String, expr: &LinearExpr) -> String {
        match expr.op {
            LinearExprOp::Ite => format!("(If({}, {}, {}))", x, y, z),
            _ => unreachable!("Operator {:?} not implemented.", expr.op),
        }
    }
}
