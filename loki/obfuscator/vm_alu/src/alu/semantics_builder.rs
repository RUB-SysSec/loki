use intermediate_language::il::assignment::Assignment;
use intermediate_language::il::expression_utils::*;
use intermediate_language::il::linearized_expressions::{LinearExpr, LinearExprOp, LinearizedExpr};
use intermediate_language::utils::bit_vecs::slice_val;
use rand::seq::SliceRandom;
use rand::thread_rng;
use rand::Rng;
use std::collections::HashSet;

#[derive(Debug, Hash, Eq, PartialEq, Clone, Ord, PartialOrd)]
pub struct SemanticsBlock {
    pub output_variable: LinearizedExpr,
    pub input_variables: Vec<LinearizedExpr>,
    pub immediate: Option<u64>,
    pub expr: LinearizedExpr,
}

impl SemanticsBlock {
    pub fn new() -> SemanticsBlock {
        unimplemented!()
    }

    fn replace_variables(expr: &mut LinearizedExpr, input_variables: &Vec<LinearizedExpr>) {
        let alu_vars = vec!["x", "y"];

        input_variables
            .iter()
            .enumerate()
            .for_each(|(index, input_var)| {
                expr.replace_var(input_var, &reg(&alu_vars[index], input_var.size()))
            });
    }

    fn replace_constant(expr: &mut LinearizedExpr) {
        let pos = expr
            .0
            .iter()
            .enumerate()
            .filter(|(_, x)| x.is_constant())
            .map(|(index, _)| index)
            .nth(0)
            .unwrap();

        let size = expr.0[pos].size;
        expr.replace_at_pos(pos, &reg("c", size));
    }

    pub fn from_assignment(assignment: &Assignment) -> SemanticsBlock {
        let input_variables = assignment.rhs.get_unique_vars();
        let output_variable = assignment.lhs.clone();
        let mut immediate = None;
        let mut expr = assignment.rhs.clone();

        // TODO: re-recheck if this still holds after superoptimization -- it doesn't!
        assert!(input_variables.len() <= 2);
        SemanticsBlock::replace_variables(&mut expr, &input_variables);

        let constants: HashSet<_> = expr
            .get_unique_constants()
            .iter()
            .map(|e| e.get_constant_val())
            .collect();
        assert!(constants.len() <= 1);

        if constants.len() == 1 {
            SemanticsBlock::replace_constant(&mut expr);
            immediate = Some(constants.into_iter().last().unwrap());
        }

        SemanticsBlock {
            input_variables,
            output_variable,
            immediate: SemanticsBlock::set_memory_constant(&expr, immediate),
            // TODO: check if this breaks s.th.
            expr: SemanticRewriter::rewrite(expr),
        }
    }

    fn set_memory_constant(expr: &LinearizedExpr, immediate: Option<u64>) -> Option<u64> {
        match expr.op().op {
            LinearExprOp::Load | LinearExprOp::Store => Some(expr.size() as u64),
            LinearExprOp::Alloc(c) => Some(c),
            _ => immediate,
        }
    }
}

pub struct SemanticsBuilder {}

impl SemanticsBuilder {
    pub fn new() -> SemanticsBuilder {
        SemanticsBuilder {}
    }

    pub fn gen_semantics(n: usize) -> Vec<LinearizedExpr> {
        (0..n)
            .map(|_| SemanticsBuilder::gen_random_semantics())
            .collect()
    }
    pub fn gen_random_semantics() -> LinearizedExpr {
        let expr_depth = thread_rng().gen::<usize>() % 3 + 1;
        SemanticsBuilder::gen_expr_with_depth(expr_depth, 64)
    }

    fn get_non_terminal_var_indices(expr: &LinearizedExpr) -> Vec<usize> {
        expr.0
            .iter()
            .enumerate()
            .filter(|(_, e)| e.is_var() && e.get_var_name() == "NT")
            .map(|(index, _)| index)
            .collect()
    }

    fn rand_var(size: usize) -> LinearizedExpr {
        let coin = thread_rng().gen::<usize>() % 6;
        match coin {
            0 => reg("x", size),
            1 => reg("y", size),
            2 => reg("c", size),
            3 => reg("k", size),
            4 => constant(0, size),
            5 => constant(1, size),
            _ => unreachable!(),
        }
    }

    fn gen_expr_with_depth(n: usize, size: usize) -> LinearizedExpr {
        /* random expression init */
        let mut expr = SemanticsBuilder::gen_expr(size);

        /* extend expression */
        for _ in 0..n {
            /* locate all non-terminal var indices in expression */
            let indices: Vec<_> = SemanticsBuilder::get_non_terminal_var_indices(&expr);

            /* choose random index */
            let rand_index = indices.choose(&mut thread_rng());

            if !rand_index.is_some() {
                return expr;
            }
            let rand_index = *rand_index.unwrap();

            /* choose random expression */
            let rand_expr = SemanticsBuilder::gen_expr(size);

            /* replace subexpression with random new expression */
            expr.replace_at_pos(rand_index, &rand_expr);
        }

        /* locate all non-terminal var indices in expression */
        let indices = SemanticsBuilder::get_non_terminal_var_indices(&expr);

        /* replace all non-terminal variables with random terminal variables */
        for index in indices {
            expr.replace_at_pos(index, &SemanticsBuilder::rand_var(size));
        }

        expr
    }

    fn gen_expr(size: usize) -> LinearizedExpr {
        /* non-terminal variables*/
        let x = reg("NT", size);
        let y = reg("NT", size);
        let z = reg("NT", size);

        let coin = thread_rng().gen::<usize>() % 14;

        match coin {
            0 => add(x, y, size),
            1 => sub(x, y, size),
            2 => mul(x, y, size),
            3 => shl_plain(x, y, size),
            4 => and(x, y, size),
            5 => or(x, y, size),
            6 => xor(x, y, size),
            7 => nand(x, y, size),
            8 => nor(x, y, size),
            9 => not(x, size),
            10 => neg(x, size),
            11 => semantics_ite(x, y, z),
            12 => check_if_zero(
                urem(
                    constant(thread_rng().gen::<u64>(), size),
                    and(reg("k", 64), constant((1 << 32) - 1, size), size),
                    size,
                ),
                64,
            ),
            13 => check_if_zero(
                sub(
                    semantics_slice(reg("k", 64), constant64(0), constant64(15), 64),
                    constant64(slice_val(thread_rng().gen(), 0 as u8, 15 as u8)),
                    64,
                ),
                64,
            )
            .simplify(),
            _ => unreachable!(),
        }
    }
}

pub struct SemanticRewriter {}

impl SemanticRewriter {
    fn rewrite(expr: LinearizedExpr) -> LinearizedExpr {
        let mut stack: Vec<LinearizedExpr> = vec![];
        for e in expr.0.into_iter() {
            let n = e.arity();
            let res = match n {
                0 => SemanticRewriter::eval_op_0(e),
                1 => SemanticRewriter::eval_op_1(stack.pop().unwrap(), e),
                2 => SemanticRewriter::eval_op_2(stack.pop().unwrap(), stack.pop().unwrap(), e),
                3 => SemanticRewriter::eval_op_3(
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
        Assignment::new(assignment.lhs, SemanticRewriter::rewrite(assignment.rhs))
    }

    fn eval_op_0(expr: LinearExpr) -> LinearizedExpr {
        match expr.op {
            LinearExprOp::Reg(ref s) => reg(s, 64),
            LinearExprOp::Const(x) => constant(x, 64),
            LinearExprOp::Alloc(c) => alloc(c, expr.size),
            _ => unreachable!("Operator {:?} not implemented.", expr.op),
        }
    }

    fn eval_op_1(x: LinearizedExpr, expr: LinearExpr) -> LinearizedExpr {
        // println!("x: {:?} -- expr: {:?}", x, expr);
        match expr.op {
            LinearExprOp::Not => semantic_downcast(not(x, 64), expr.size),
            LinearExprOp::Neg => semantic_downcast(neg(x, 64), expr.size),
            LinearExprOp::ZeroExtend => semantic_downcast(zero_extend(x, 64), expr.size),
            LinearExprOp::SignExtend => unreachable!(),
            /* used to extract the LSB (for EQUAL comparisons returning 1 bit) */
            LinearExprOp::Slice(..) => semantic_downcast(x.clone(), expr.size),
            LinearExprOp::Load => load(x, expr.size),
            LinearExprOp::Mem => mem(x, expr.size),
            _ => unreachable!("Operator {:?} not implemented.", expr.op),
        }
    }

    fn eval_op_2(y: LinearizedExpr, x: LinearizedExpr, expr: LinearExpr) -> LinearizedExpr {
        // println!("x: {:?} -- y: {:?} -- expr: {:?}", x, y, expr);
        match expr.op {
            LinearExprOp::Add => semantic_downcast(add(x, y, 64), expr.size),
            LinearExprOp::Sub => semantic_downcast(sub(x, y, 64), expr.size),
            LinearExprOp::Mul => semantic_downcast(mul(x, y, 64), expr.size),
            LinearExprOp::Udiv => semantic_downcast(udiv(x, y, 64), expr.size),
            LinearExprOp::Sdiv => semantic_downcast(sdiv(x, y, 64), expr.size),
            LinearExprOp::Urem => semantic_downcast(urem(x, y, 64), expr.size),
            LinearExprOp::Srem => semantic_downcast(srem(x, y, 64), expr.size),
            LinearExprOp::Shl => semantic_downcast(shl_plain(x, y, 64), expr.size),
            LinearExprOp::Lshr => semantic_downcast(lshr_plain(x, y, 64), expr.size),
            /*
             * This won't work if MSB is set and size < 64. Operation is on 64-bit, i.e., 1 is added on pos 63.
             * However, we downcast this to 32 bit (or any size < 64) by throwing aways pos 32 to 63 (through AND),
             * thereby effectively turning this into a LShr instead of an AShr.
             */
            LinearExprOp::Ashr => semantic_downcast(ashr_plain(x, y, 64), expr.size),
            LinearExprOp::And => semantic_downcast(and(x, y, 64), expr.size),
            LinearExprOp::Or => semantic_downcast(or(x, y, 64), expr.size),
            LinearExprOp::Xor => semantic_downcast(xor(x, y, 64), expr.size),
            LinearExprOp::Nand => unreachable!(),
            LinearExprOp::Nor => unreachable!(),
            LinearExprOp::Ult => semantic_downcast(ult(x, y, 64), expr.size),
            LinearExprOp::Slt => semantic_downcast(slt(x, y, 64), expr.size),
            LinearExprOp::Ule => semantic_downcast(ule(x, y, 64), expr.size),
            LinearExprOp::Sle => semantic_downcast(sle(x, y, 64), expr.size),
            LinearExprOp::Equal => semantic_downcast(equal(x, y, 64), expr.size),
            LinearExprOp::Store => store(x, y, expr.size),
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
            LinearExprOp::Ite => unreachable!(),
            _ => unreachable!("Operator {:?} not implemented.", expr.op),
        }
    }
}
