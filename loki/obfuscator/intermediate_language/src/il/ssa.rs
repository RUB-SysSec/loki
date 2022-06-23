use il::assignment::Assignment;
use il::expression_utils::*;
use il::linearized_expressions::{LinearExpr, LinearExprOp, LinearizedExpr};
use FastHashMap;

pub struct SSA {
    var_stack: FastHashMap<String, u64>,
}

impl SSA {
    pub fn new() -> SSA {
        SSA {
            var_stack: FastHashMap::default(),
        }
    }

    pub fn from_assignments(assignments: &Vec<Assignment>) -> Vec<Assignment> {
        let mut ssa = SSA::new();
        let mut ret = vec![];

        for assignment in assignments {
            let flattened = ssa.flatten_expr(&assignment.rhs);
            for flatten in flattened {
                ret.push(flatten)
            }

            let lhs = ssa.var_lhs(&assignment.lhs.get_var_name(), assignment.size);
            ret.push(Assignment::new(
                lhs,
                ssa.temp_var_rhs(assignment.lhs.size()),
            ));
        }

        ret
    }

    fn var_lhs(&mut self, var_name: &str, size: usize) -> LinearizedExpr {
        let count = self.var_stack.entry(var_name.to_string()).or_insert(0);
        *count += 1;

        reg(&format!("{}{}", var_name, count), size)
    }

    fn var_rhs(&self, var_name: &str, size: usize) -> LinearizedExpr {
        match self.var_stack.contains_key(var_name) {
            true => reg(&format!("{}{}", var_name, self.var_stack[var_name]), size),
            false => reg(var_name, size),
        }
    }

    fn temp_var_name() -> String {
        "T".to_string()
    }

    fn temp_var_lhs(&mut self, size: usize) -> LinearizedExpr {
        self.var_lhs(&SSA::temp_var_name(), size)
    }

    fn temp_var_rhs(&self, size: usize) -> LinearizedExpr {
        self.var_rhs(&SSA::temp_var_name(), size)
    }

    pub fn flatten_expr(&mut self, expr: &LinearizedExpr) -> Vec<Assignment> {
        let mut replacements: FastHashMap<LinearizedExpr, LinearizedExpr> = FastHashMap::default();

        let mut stack = vec![];
        let mut res = vec![];
        for e in expr.0.iter() {
            let n = e.arity();
            let rhs = match n {
                0 => self.eval_op_0(e),
                1 => self.eval_op_1(&stack.pop().unwrap(), e),
                2 => self.eval_op_2(&stack.pop().unwrap(), &stack.pop().unwrap(), e),
                3 => self.eval_op_3(
                    &stack.pop().unwrap(),
                    &stack.pop().unwrap(),
                    &stack.pop().unwrap(),
                    e,
                ),
                _ => unreachable!(),
            };

            if let Some(entry) = replacements.get(&rhs) {
                stack.push(entry.clone());
            } else {
                let assignment = Assignment::new(self.temp_var_lhs(rhs.size()), rhs);
                stack.push(self.temp_var_rhs(assignment.size));
                replacements.insert(assignment.rhs.clone(), assignment.lhs.clone());

                res.push(assignment);
            }
        }
        assert_eq!(stack.len(), 1);
        res
    }

    fn eval_op_0(&self, expr: &LinearExpr) -> LinearizedExpr {
        match expr.op {
            LinearExprOp::Reg(ref s) => self.var_rhs(s, expr.size),
            LinearExprOp::Const(x) => constant(x, expr.size),
            LinearExprOp::Nop => nop(expr.size),
            LinearExprOp::Alloc(c) => alloc(c, expr.size),
            _ => unreachable!("Operator {:?} not implemented.", expr.op),
        }
    }

    fn eval_op_1(&self, x: &LinearizedExpr, expr: &LinearExpr) -> LinearizedExpr {
        match expr.op {
            LinearExprOp::Not => build_op_1(x, expr, not),
            LinearExprOp::Neg => build_op_1(x, expr, neg),
            LinearExprOp::Slice(start, end) => slice(x.clone(), start, end),
            LinearExprOp::ZeroExtend => build_op_1(x, expr, zero_extend),
            LinearExprOp::SignExtend => build_op_1(x, expr, sign_extend),
            LinearExprOp::Load => build_op_1(x, expr, load),
            LinearExprOp::Mem => build_op_1(x, expr, mem),
            _ => unreachable!("Operator {:?} not implemented.", expr.op),
        }
    }

    fn eval_op_2(
        &self,
        y: &LinearizedExpr,
        x: &LinearizedExpr,
        expr: &LinearExpr,
    ) -> LinearizedExpr {
        match expr.op {
            LinearExprOp::Add => build_op_2(x, y, expr, add),
            LinearExprOp::Sub => build_op_2(x, y, expr, sub),
            LinearExprOp::Mul => build_op_2(x, y, expr, mul),
            LinearExprOp::Udiv => build_op_2(x, y, expr, udiv),
            LinearExprOp::Sdiv => build_op_2(x, y, expr, sdiv),
            LinearExprOp::Urem => build_op_2(x, y, expr, urem),
            LinearExprOp::Srem => build_op_2(x, y, expr, srem),
            LinearExprOp::Shl => build_op_2(x, y, expr, shl_plain),
            LinearExprOp::Lshr => build_op_2(x, y, expr, lshr_plain),
            LinearExprOp::Ashr => build_op_2(x, y, expr, ashr_plain),
            LinearExprOp::And => build_op_2(x, y, expr, and),
            LinearExprOp::Or => build_op_2(x, y, expr, or),
            LinearExprOp::Xor => build_op_2(x, y, expr, xor),
            LinearExprOp::Nand => build_op_2(x, y, expr, nand),
            LinearExprOp::Nor => build_op_2(x, y, expr, nor),
            LinearExprOp::Ult => build_op_2(x, y, expr, ult),
            LinearExprOp::Slt => build_op_2(x, y, expr, slt),
            LinearExprOp::Ule => build_op_2(x, y, expr, ule),
            LinearExprOp::Sle => build_op_2(x, y, expr, sle),
            LinearExprOp::Equal => build_op_2(x, y, expr, equal),
            LinearExprOp::Concat => concat(x.clone(), y.clone()),
            LinearExprOp::Store => build_op_2(x, y, expr, store),
            _ => unreachable!("Operator {:?} not implemented.", expr.op),
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
            LinearExprOp::Ite => build_op_3(x, y, z, expr, ite),
            _ => unreachable!("Operator {:?} not implemented.", expr.op),
        }
    }
}

fn build_op_1<F>(x: &LinearizedExpr, expr: &LinearExpr, f: F) -> LinearizedExpr
where
    F: Fn(LinearizedExpr, usize) -> LinearizedExpr,
{
    f(x.clone(), expr.size)
}

fn build_op_2<F>(x: &LinearizedExpr, y: &LinearizedExpr, expr: &LinearExpr, f: F) -> LinearizedExpr
where
    F: Fn(LinearizedExpr, LinearizedExpr, usize) -> LinearizedExpr,
{
    f(x.clone(), y.clone(), expr.size)
}

fn build_op_3<F>(
    x: &LinearizedExpr,
    y: &LinearizedExpr,
    z: &LinearizedExpr,
    expr: &LinearExpr,
    f: F,
) -> LinearizedExpr
where
    F: Fn(LinearizedExpr, LinearizedExpr, LinearizedExpr, usize) -> LinearizedExpr,
{
    f(x.clone(), y.clone(), z.clone(), expr.size)
}
