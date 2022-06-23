use intermediate_language::il::assignment::Assignment;
use intermediate_language::il::linearized_expressions::{LinearExpr, LinearExprOp, LinearizedExpr};

pub struct LLVMTranslator {}

impl LLVMTranslator {
    pub fn translate(expr: &LinearizedExpr) -> String {
        let mut stack = vec![];
        for e in expr.0.iter() {
            let n = e.arity();
            let res = match n {
                0 => LLVMTranslator::eval_op_0(e),
                1 => LLVMTranslator::eval_op_1(&stack.pop().unwrap(), e),
                2 => LLVMTranslator::eval_op_2(&stack.pop().unwrap(), &stack.pop().unwrap(), e),
                3 => LLVMTranslator::eval_op_3(
                    &stack.pop().unwrap(),
                    &stack.pop().unwrap(),
                    &stack.pop().unwrap(),
                    e,
                ),
                _ => unreachable!(),
            };
            stack.push(res);
        }
        assert_eq!(stack.len(), 1);
        stack.pop().unwrap()
    }

    pub fn from_alu(alu: &Vec<Assignment>) -> String {
        LLVMTranslator::from_ssa_assignments(&alu.as_slice()[0..alu.len() - 1])
    }

    pub fn from_ssa_assignments(assignmnets: &[Assignment]) -> String {
        assignmnets
            .iter()
            .map(|i| {
                format!(
                    "{} = {}\n",
                    i.lhs.get_var_name(),
                    LLVMTranslator::translate(&i.rhs)
                )
            })
            .collect()
    }

    fn eval_op_0(expr: &LinearExpr) -> String {
        match expr.op {
            LinearExprOp::Reg(ref s) => format!("REG {} {}", expr.size, s.to_string()),
            LinearExprOp::Const(x) => format!("INT {} 0x{:x}", expr.size, x),
            LinearExprOp::Nop => format!("NOP"),
            _ => unreachable!("Operator {:?} not implemented.", expr.op),
        }
    }

    fn eval_op_1(x: &String, expr: &LinearExpr) -> String {
        match expr.op {
            LinearExprOp::Not => format!("NOT {} {}", expr.size, x),
            LinearExprOp::Neg => format!("NEG {} {}", expr.size, x),
            LinearExprOp::ZeroExtend => format!("ZEXT {} {}", expr.size, x),
            LinearExprOp::SignExtend => format!("SEXT {} {}", expr.size, x),
            LinearExprOp::Slice(..) => unreachable!("Operator {:?}: never emit directly!", expr.op),
            LinearExprOp::Load => format!("LOAD {} {}", expr.size, x),
            _ => unreachable!("Operator {:?} not implemented.", expr.op),
        }
    }

    fn eval_op_2(y: &String, x: &String, expr: &LinearExpr) -> String {
        match expr.op {
            LinearExprOp::Add => format!("ADD {} {} {}", expr.size, x, y),
            LinearExprOp::Sub => format!("SUB {} {} {}", expr.size, x, y),
            LinearExprOp::And => format!("AND {} {} {}", expr.size, x, y),
            LinearExprOp::Or => format!("OR {} {} {}", expr.size, x, y),
            LinearExprOp::Xor => format!("XOR {} {} {}", expr.size, x, y),
            LinearExprOp::Shl => format!("SHL {} {} {}", expr.size, x, y),
            LinearExprOp::Lshr => format!("LSHR {} {} {}", expr.size, x, y),
            LinearExprOp::Ashr => format!("ASHR {} {} {}", expr.size, x, y),
            LinearExprOp::Equal => format!("ICMPEQ {} {} {}", expr.size, x, y),
            LinearExprOp::Mul => format!("MUL {} {} {}", expr.size, x, y),
            LinearExprOp::Udiv => format!("UDIV {} {} {}", expr.size, x, y),
            LinearExprOp::Sdiv => format!("SDIV {} {} {}", expr.size, x, y),
            LinearExprOp::Urem => format!("UREM {} {} {}", expr.size, x, y),
            LinearExprOp::Srem => format!("SREM {} {} {}", expr.size, x, y),
            LinearExprOp::Ult => format!("ULT {} {} {}", expr.size, x, y),
            LinearExprOp::Slt => format!("SLT {} {} {}", expr.size, x, y),
            LinearExprOp::Ule => format!("ULE {} {} {}", expr.size, x, y),
            LinearExprOp::Sle => format!("SLE {} {} {}", expr.size, x, y),
            /* TODO */
            LinearExprOp::Mem => unimplemented!(),
            LinearExprOp::Nor | LinearExprOp::Nand | LinearExprOp::Concat => {
                unreachable!("Operator {:?}: never emit directly!", expr.op)
            }
            _ => unreachable!("Operator {:?} not implemented.", expr.op),
        }
    }

    fn eval_op_3(z: &String, y: &String, x: &String, expr: &LinearExpr) -> String {
        match expr.op {
            LinearExprOp::Ite => format!("ITE {} {} {} {}", expr.size, x, y, z),
            _ => unreachable!("Operator {:?} not implemented.", expr.op),
        }
    }
}
