use intermediate_language::il::assignment::Assignment;
use intermediate_language::il::expression_utils::*;
use intermediate_language::il::expression_utils::{add, constant};
use intermediate_language::il::linearized_expressions::{LinearExpr, LinearExprOp, LinearizedExpr};

pub struct InputEmulationPreprocessor {}

impl InputEmulationPreprocessor {
    pub fn new() -> Self {
        InputEmulationPreprocessor {}
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
        match assignment.rhs.is_var() || assignment.rhs.is_constant() {
            true => Assignment::new(assignment.lhs, assignment.rhs.clone()),
            false if assignment.rhs.op().op == LinearExprOp::Store => {
                /* rewrite store on LHS to @size[address] */
                Assignment::new(
                    mem(
                        zero_extend(
                            LinearizedExpr::from_linear_expr(
                                assignment.rhs.0.first().unwrap().clone(),
                            )
                            .simplify(),
                            64,
                        ),
                        assignment.rhs.size(),
                    ),
                    self.rewrite(assignment.rhs),
                )
            }
            false => Assignment::new(assignment.lhs, self.rewrite(assignment.rhs)),
        }
    }

    pub fn rewrite_assignments(assignments: Vec<Assignment>) -> Vec<Assignment> {
        let mut postprocessor = InputEmulationPreprocessor::new();
        let mut ret: Vec<Assignment> = assignments
            .into_iter()
            .map(|assignment| postprocessor.rewrite_assignment(assignment))
            .collect();

        let size = ret
            .last()
            .expect("Assignment vector should not be empty")
            .size;

        // ret = SSA::from_assignments(&ret);

        let lhs = reg("out_reg", size);
        let rhs = ret.last().unwrap().lhs.clone();
        ret.push(Assignment::new(lhs, rhs));

        ret
    }

    fn eval_op_0(&self, expr: LinearExpr) -> LinearizedExpr {
        match expr.op {
            LinearExprOp::Reg(ref s) => reg(s, expr.size),
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
            LinearExprOp::SignExtend => sign_extend(x, expr.size),

            LinearExprOp::Trunc => slice(x, 0, (expr.size - 1) as u8),
            LinearExprOp::Load => {
                assert_eq!(x.size(), 64);
                mem(x.simplify(), expr.size)
            }

            LinearExprOp::Alloca => alloc(x.get_constant_val(), expr.size),
            LinearExprOp::BitCast if x.size() == expr.size => {
                add(x, constant(0, expr.size), expr.size)
            }
            LinearExprOp::BitCast if x.size() < expr.size => zero_extend(x, expr.size),
            LinearExprOp::Slice(..) => unreachable!(),
            _ => unreachable!("Operator {:?} not implemented.", expr.op),
        }
    }

    fn eval_op_2(&self, y: LinearizedExpr, x: LinearizedExpr, expr: LinearExpr) -> LinearizedExpr {
        // println!("x: {:?} -- y: {:?} -- op: {:?}", x, y, expr);
        /* preprocessing */
        // let mut to_lsb = false;
        // // If size imported from LLVM is 1 for EQUAL (i.e., result of bit comparison), then upcast the size to one of the operand's size (to avoid size mismatch) and mark expression for (semantic) least-significant bit extraction (i.e., we model the bit comparison by extracting the LSB of the upcasted comparison)
        // match expr.op {
        //     LinearExprOp::Ult
        //     | LinearExprOp::Slt
        //     | LinearExprOp::Ule
        //     | LinearExprOp::Sle
        //     | LinearExprOp::Equal
        //         if expr.size == 1 =>
        //     {
        //         expr.size = x.size();
        //         to_lsb = true;
        //     }
        //     _ => {}
        // }

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
            LinearExprOp::Sdiv => sdiv(x, y, expr.size),
            LinearExprOp::Urem => urem(x, y, expr.size),
            LinearExprOp::Srem => srem(x, y, expr.size),
            LinearExprOp::Shl => shl_plain(x, y, expr.size),
            LinearExprOp::Lshr => lshr_plain(x, y, expr.size),
            LinearExprOp::Ashr => ashr_plain(x, y, expr.size),
            LinearExprOp::And => and(x, y, expr.size),
            LinearExprOp::Or => or(x, y, expr.size),
            LinearExprOp::Xor => xor(x, y, expr.size),
            // LinearExprOp::Ult if to_lsb => lsb(ult(x, y, expr.size)),
            // LinearExprOp::Ult => ult(x, y, expr.size),
            // LinearExprOp::Slt if to_lsb => lsb(slt(
            //     semantic_sign_extension(x, 64),
            //     semantic_sign_extension(y, 64),
            //     64,
            // )),
            // LinearExprOp::Slt => {
            //     LLVMInputDataPostProcessor::wrap_semantic_sign_extension(slt, x, y, expr.size)
            // }
            // LinearExprOp::Ule if to_lsb => lsb(ule(x, y, expr.size)),
            // LinearExprOp::Ule => ule(x, y, expr.size),
            // LinearExprOp::Sle if to_lsb => lsb(sle(
            //     semantic_sign_extension(x, 64),
            //     semantic_sign_extension(y, 64),
            //     64,
            // )),
            // LinearExprOp::Sle => {
            //     LLVMInputDataPostProcessor::wrap_semantic_sign_extension(sle, x, y, expr.size)
            // }
            // LinearExprOp::Equal if to_lsb => lsb(equal(x, y, expr.size)),
            // LinearExprOp::Equal => equal(x, y, expr.size),
            LinearExprOp::Concat => unreachable!(),
            LinearExprOp::GEP => add(x, y, expr.size),
            LinearExprOp::Store => {
                assert_eq!(x.size(), 64);
                assert_eq!(y.size(), expr.size);
                y
            }
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
            LinearExprOp::Ite => ite(x, y, z, expr.size),
            _ => unreachable!("Operator {:?} not implemented.", expr.op),
        }
    }
}
