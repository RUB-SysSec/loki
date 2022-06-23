use intermediate_language::il::assignment::Assignment;
use intermediate_language::il::expression_utils::*;
use intermediate_language::il::expression_utils::{add, constant};
use intermediate_language::il::linearized_expressions::{LinearExpr, LinearExprOp, LinearizedExpr};
use intermediate_language::il::ssa::SSA;
use std::collections::HashSet;

pub struct LLVMInputDataPostProcessor {
    input_arguments: HashSet<String>,
    seen: HashSet<String>,
}

impl LLVMInputDataPostProcessor {
    pub fn new(input_arguments: &Vec<String>) -> LLVMInputDataPostProcessor {
        LLVMInputDataPostProcessor {
            input_arguments: input_arguments.iter().cloned().collect(),
            seen: input_arguments.iter().cloned().collect(),
        }
    }
    fn rewrite(&self, expr: LinearizedExpr) -> LinearizedExpr {
        let mut stack: Vec<LinearizedExpr> = vec![];
        for e in expr.0.into_iter() {
            let n = e.arity();
            let res = match n {
                0 => self.eval_op_0(e),
                1 => self.eval_op_1(stack.pop().unwrap(), e),
                2 => self.eval_op_2(stack.pop().unwrap(), stack.pop().unwrap(), e),
                3 => self.eval_op_3(
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

    pub fn rewrite_assignment(&mut self, assignment: Assignment) -> Assignment {
        match &assignment.lhs.op().op {
            LinearExprOp::Reg(s) => self.seen.insert(s.clone()),
            _ => unreachable!(),
        };
        match assignment.rhs.is_var() || assignment.rhs.is_constant() {
            true => Assignment::new(assignment.lhs, assignment.rhs.clone()),
            false => Assignment::new(assignment.lhs, self.rewrite(assignment.rhs)),
        }
    }

    pub fn rewrite_assignments(
        assignments: Vec<Assignment>,
        input_arguments: &Vec<String>,
    ) -> Vec<Assignment> {
        let mut postprocessor = LLVMInputDataPostProcessor::new(input_arguments);
        let mut ret: Vec<Assignment> = assignments
            .into_iter()
            .map(|assignment| postprocessor.rewrite_assignment(assignment))
            .collect();

        let size = ret
            .last()
            .expect("Assignment vector should not be empty")
            .size;

        ret = SSA::from_assignments(&ret);

        let lhs = reg("out_reg", size);
        let rhs = ret.last().unwrap().lhs.clone();
        ret.push(Assignment::new(lhs, rhs));
        ret
    }

    fn eval_op_0(&self, expr: LinearExpr) -> LinearizedExpr {
        match expr.op {
            LinearExprOp::Reg(ref s) if expr.size != 64 && self.input_arguments.contains(s) => {
                semantic_downcast(reg(s, expr.size), expr.size)
            }
            LinearExprOp::Reg(ref s) if self.seen.contains(s) => reg(s, expr.size),
            LinearExprOp::Reg(ref s) => unreachable!("access to unknown variable {}", s),
            LinearExprOp::Const(x) => constant(x, expr.size),
            _ => unreachable!("Operator {:?} not implemented.", expr.op),
        }
    }

    fn eval_op_1(&self, x: LinearizedExpr, expr: LinearExpr) -> LinearizedExpr {
        // println!("x: {:?} -- op: {:?}", x, expr);
        match expr.op {
            LinearExprOp::ZeroExtend | LinearExprOp::SignExtend | LinearExprOp::Trunc => {}
            LinearExprOp::Load => {}
            _ => assert_eq!(x.size(), expr.size),
        }
        match expr.op {
            LinearExprOp::Not => not(x, expr.size),
            LinearExprOp::Neg => neg(x, expr.size),
            LinearExprOp::ZeroExtend => zero_extend(x, expr.size),
            LinearExprOp::SignExtend => {
                slice(semantic_sign_extension(x, 64), 0, (expr.size - 1) as u8)
            }
            LinearExprOp::Trunc => slice(x, 0, (expr.size - 1) as u8),
            LinearExprOp::Load => load(x, expr.size),
            LinearExprOp::Alloca if x.is_constant() => alloc(x.get_constant_val(), expr.size),
            LinearExprOp::BitCast if x.size() == expr.size => {
                add(x, constant(0, expr.size), expr.size)
            }
            LinearExprOp::BitCast if x.size() < expr.size => zero_extend(x, expr.size),
            LinearExprOp::Slice(..) => unreachable!(),
            _ => unreachable!("Operator {:?} not implemented.", expr.op),
        }
    }

    fn eval_op_2(
        &self,
        y: LinearizedExpr,
        x: LinearizedExpr,
        mut expr: LinearExpr,
    ) -> LinearizedExpr {
        // println!("x: {:?} -- y: {:?} -- op: {:?}", x, y, expr);
        /* preprocessing */
        let mut to_lsb = false;
        // If size imported from LLVM is 1 for EQUAL (i.e., result of bit comparison), then upcast the size to one of the operand's size (to avoid size mismatch) and mark expression for (semantic) least-significant bit extraction (i.e., we model the bit comparison by extracting the LSB of the upcasted comparison)
        match expr.op {
            LinearExprOp::Ult
            | LinearExprOp::Slt
            | LinearExprOp::Ule
            | LinearExprOp::Sle
            | LinearExprOp::Equal
                if expr.size == 1 =>
            {
                expr.size = x.size();
                to_lsb = true;
            }
            _ => {}
        }

        // println!("x: {:?} -- y: {:?} -- op: {:?}", x, y, expr);
        /* size checks */
        match expr.op {
            LinearExprOp::Store => {
                assert_eq!(x.size(), 64, "memory address should be 64 bit");
                assert_eq!(y.size(), expr.size, "memory write should match store size");
            }
            _ => {
                assert_eq!(x.size(), y.size());
                assert_eq!(y.size(), expr.size);
            }
        }

        match expr.op {
            LinearExprOp::Add => add(x, y, expr.size),
            LinearExprOp::Sub => sub(x, y, expr.size),
            LinearExprOp::Mul => mul(x, y, expr.size),
            LinearExprOp::Udiv => udiv(x, y, expr.size),
            LinearExprOp::Sdiv => {
                LLVMInputDataPostProcessor::wrap_semantic_sign_extension(sdiv, x, y, expr.size)
            }
            LinearExprOp::Urem => urem(x, y, expr.size),
            LinearExprOp::Srem => {
                LLVMInputDataPostProcessor::wrap_semantic_sign_extension(srem, x, y, expr.size)
            }
            LinearExprOp::Shl => shl_plain(x, y, expr.size),
            LinearExprOp::Lshr => lshr_plain(x, y, expr.size),
            LinearExprOp::Ashr => LLVMInputDataPostProcessor::wrap_semantic_sign_extension(
                ashr_plain, x, y, expr.size,
            ),
            LinearExprOp::And => and(x, y, expr.size),
            LinearExprOp::Or => or(x, y, expr.size),
            LinearExprOp::Xor => xor(x, y, expr.size),
            LinearExprOp::Ult if to_lsb => lsb(ult(x, y, expr.size)),
            LinearExprOp::Ult => ult(x, y, expr.size),
            LinearExprOp::Slt if to_lsb => lsb(slt(
                semantic_sign_extension(x, 64),
                semantic_sign_extension(y, 64),
                64,
            )),
            LinearExprOp::Slt => {
                LLVMInputDataPostProcessor::wrap_semantic_sign_extension(slt, x, y, expr.size)
            }
            LinearExprOp::Ule if to_lsb => lsb(ule(x, y, expr.size)),
            LinearExprOp::Ule => ule(x, y, expr.size),
            LinearExprOp::Sle if to_lsb => lsb(sle(
                semantic_sign_extension(x, 64),
                semantic_sign_extension(y, 64),
                64,
            )),
            LinearExprOp::Sle => {
                LLVMInputDataPostProcessor::wrap_semantic_sign_extension(sle, x, y, expr.size)
            }
            LinearExprOp::Equal if to_lsb => lsb(equal(x, y, expr.size)),
            LinearExprOp::Equal => equal(x, y, expr.size),
            LinearExprOp::Concat => unreachable!(),
            LinearExprOp::GEP => add(x, y, expr.size),
            LinearExprOp::Store => store(x, y, expr.size),
            LinearExprOp::Nand => unreachable!(),
            LinearExprOp::Nor => unreachable!(),
            _ => unreachable!("Operator {:?} not implemented.", expr.op),
        }
    }

    fn eval_op_3(
        &self,
        z: LinearizedExpr,
        y: LinearizedExpr,
        x: LinearizedExpr,
        expr: LinearExpr,
    ) -> LinearizedExpr {
        assert_eq!(y.size(), z.size());
        assert_eq!(y.size(), expr.size);
        match expr.op {
            LinearExprOp::Ite => semantics_ite(x, y, z),
            _ => unreachable!("Operator {:?} not implemented.", expr.op),
        }
    }

    /*
     * Wraps semantic_sign_extension in expression_utils. Semantic_sign_extension is requried to guarantee that signed operations
     * on operands with size smaller than 64 bit work correctly in the 64-bit setting of the ALU. To this end, the operands are
     * sign-extended (by mimicking sign_extend with other operands to avoid optimization removing it) before the result is sliced
     * down to its original size (thereby discarding the sign-extension), such that following operations may work correctly.
     */
    fn wrap_semantic_sign_extension(
        f: fn(LinearizedExpr, LinearizedExpr, usize) -> LinearizedExpr,
        x: LinearizedExpr,
        y: LinearizedExpr,
        expr_size: usize,
    ) -> LinearizedExpr {
        slice(
            f(
                semantic_sign_extension(x, 64),
                semantic_sign_extension(y, 64),
                64,
            ),
            0,
            (expr_size - 1) as u8,
        )
    }
}
