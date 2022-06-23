use il::expression_utils::*;
use il::linearized_expressions::*;
use symbolic_execution::se_helper::split_into_args;
use symbolic_execution::se_helper::*;
use utils::bit_vecs::{concat_val, mask_to_size, sign_extend, slice_val};

pub fn simplify_op_1<F>(x: &LinearizedExpr, op: &LinearExpr, f: F) -> LinearizedExpr
where
    F: Fn(u64) -> u64,
{
    if x.is_constant() {
        return simplify_const_op_1(x, f);
    }

    match op.op {
        // - (- x) => x
        LinearExprOp::Neg if x.op().op == LinearExprOp::Neg => {
            return x.get_expression_slice(0, x.len() - 1)
        }
        // ~ (~ x) => x
        LinearExprOp::Not if x.op().op == LinearExprOp::Not => {
            return x.get_expression_slice(0, x.len() - 1)
        }
        _ => {}
    }

    LinearizedExpr::new(build_args_op_1(x.to_vec(), op.clone()))
}

pub fn no_simplification_op_1(x: &LinearizedExpr, op: &LinearExpr) -> LinearizedExpr {
    LinearizedExpr::new(build_args_op_1(x.to_vec(), op.clone()))
}

pub fn no_simplification_op_2(
    x: &LinearizedExpr,
    y: &LinearizedExpr,
    op: &LinearExpr,
) -> LinearizedExpr {
    LinearizedExpr::new(build_args_op_2(x.to_vec(), y.to_vec(), op.clone()))
}

pub fn no_simplification_op_3(
    x: &LinearizedExpr,
    y: &LinearizedExpr,
    z: &LinearizedExpr,
    op: &LinearExpr,
) -> LinearizedExpr {
    LinearizedExpr::new(build_args_op_3(
        x.to_vec(),
        y.to_vec(),
        z.to_vec(),
        op.clone(),
    ))
}

pub fn simplify_op_2<F>(
    x: &LinearizedExpr,
    y: &LinearizedExpr,
    op: &LinearExpr,
    f: F,
) -> LinearizedExpr
where
    F: Fn(u64, u64) -> u64,
{
    if x.is_constant() && y.is_constant() {
        return simplify_const_op_2(x, y, f);
    }

    match op.op {
        // x - x => 0
        LinearExprOp::Sub if x == y && !x.is_non_terminal() => return constant(0, op.size),
        // x - 0 => x
        LinearExprOp::Sub if y.check_constant_val(0) => return x.clone(),
        // 0 - y => - y
        LinearExprOp::Sub if x.check_constant_val(0) => return neg(y.clone(), y.size()),
        // x - (-y) => x + y
        LinearExprOp::Sub if y.op().op == LinearExprOp::Neg => {
            return add(x.clone(), y.get_expression_slice(0, y.len() - 1), op.size)
        }
        // x - y => x + (-y)
        LinearExprOp::Sub => return add(x.clone(), neg(y.clone(), op.size), op.size),
        // x << 0 => x
        LinearExprOp::Shl if y.check_constant_val(0) => return x.clone(),
        // 0 << y => 0
        LinearExprOp::Shl if x.check_constant_val(0) => return constant(0, op.size),

        // 0 >> y => 0
        LinearExprOp::Lshr if x.check_constant_val(0) => return constant(0, op.size),
        // x >> 0 => x
        LinearExprOp::Lshr if y.check_constant_val(0) => return x.clone(),

        // x < x => 0
        LinearExprOp::Ult if !x.is_non_terminal() && x == y => return constant(0, op.size),
        // x <s x => 0
        LinearExprOp::Slt if !x.is_non_terminal() && x == y => return constant(0, op.size),
        // x <= x => 1
        LinearExprOp::Ule if !x.is_non_terminal() && x == y => return constant(1, op.size),
        // x <=s x => 1
        LinearExprOp::Sle if !x.is_non_terminal() && x == y => return constant(1, op.size),
        // x == x => 1
        LinearExprOp::Equal if !x.is_non_terminal() && x == y => return constant(1, op.size),
        _ => {}
    }

    LinearizedExpr::new(build_args_op_2(x.to_vec(), y.to_vec(), op.clone()))
}

pub fn simplify_commutative_op_2<F>(
    x: &LinearizedExpr,
    y: &LinearizedExpr,
    op: &LinearExpr,
    f: F,
) -> LinearizedExpr
where
    F: Fn(u64, u64) -> u64,
{
    //    println!("x: {:?} -- y: {:?} -- op: {:?}", x,y,op);
    let (x, y) = normalize(x, y);

    /* arithmetic identities */
    match (&op.op, x.is_constant(), y.is_constant()) {
        // const op const => const
        (_, true, true) => return simplify_const_op_2(x, y, f),

        // x + 0 => x
        (LinearExprOp::Add, false, true) if y.get_constant_val() == 0 => return x.clone(),

        // x + (-x) => 0
        (LinearExprOp::Add, _, _)
            if !x.is_non_terminal()
                && y.op().op == LinearExprOp::Neg
                && x.0[0..x.len()] == y.0[0..y.len() - 1] =>
        {
            return constant(0, op.size)
        }

        // x * 0 => 0
        (LinearExprOp::Mul, false, true) if y.get_constant_val() == 0 => {
            return constant(0, op.size)
        }
        // x * 1 => x
        (LinearExprOp::Mul, false, true) if y.get_constant_val() == 1 => return x.clone(),

        // x | x => x
        (LinearExprOp::Or, false, false) if x == y && !x.is_non_terminal() => return x.clone(),
        // x | 0 => x
        (LinearExprOp::Or, false, true) if y.get_constant_val() == 0 => return x.clone(),

        // x & x => x
        (LinearExprOp::And, false, false) if x == y && !x.is_non_terminal() => return x.clone(),
        // x & 0 => 0
        (LinearExprOp::And, false, true) if y.get_constant_val() == 0 => {
            return constant(0, op.size);
        }
        // x ^ x => 0
        (LinearExprOp::Xor, false, false) if x == y && !x.is_non_terminal() => {
            return constant(0, op.size)
        }
        // x ^ 0 => x
        (LinearExprOp::Xor, false, true) if y.get_constant_val() == 0 => return x.clone(),

        // x NAND 0 => -1
        (LinearExprOp::Nand, false, true) if y.get_constant_val() == 0 => {
            return neg(constant(1, op.size), op.size)
        }
        // x NAND x => !x
        (LinearExprOp::Nand, false, false) if !x.is_non_terminal() && x == y => {
            return not(x.clone(), op.size)
        }

        // x NOR 0 => !x
        (LinearExprOp::Nor, false, true) if y.get_constant_val() == 0 => {
            return not(x.clone(), op.size)
        }
        // x NOR x => !x
        (LinearExprOp::Nor, false, false) if !x.is_non_terminal() && x == y => {
            return not(x.clone(), op.size)
        }

        // (u op const) op const => u op (const op const) => u op const
        (_, false, true) if x.op() == op && op.is_associative() => {
            let args = split_into_args(x);
            assert_eq!(args.len(), 2);
            let (v, w) = normalize(&args[0], &args[1]);
            if !v.is_constant() && w.is_constant() {
                let constant = simplify_const_op_2(y, w, f);
                return build_op_2(v, &constant, op);
            }
        }
        _ => {}
    }

    build_op_2(x, y, op)
}

pub fn simplify_zero_extend(x: &LinearizedExpr, op: &LinearExpr) -> LinearizedExpr {
    //    println!("x: {:?} -- op: {:?}", x, op);
    assert!(x.size() <= op.size);
    if x.is_constant() {
        let mut constant = simplify_const_op_1(x, |v| v);
        constant.set_size(op.size);
        return constant;
    }
    if x.size() == op.size {
        return x.clone();
    }
    LinearizedExpr::new(build_args_op_1(x.to_vec(), op.clone()))
}

pub fn simplify_sign_extend(x: &LinearizedExpr, op: &LinearExpr) -> LinearizedExpr {
    assert!(x.size() <= op.size);
    if x.is_constant() {
        let val = sign_extend(x.get_constant_val(), x.size(), op.size);
        return LinearizedExpr::from_linear_expr(LinearExpr::new(
            LinearExprOp::Const(val),
            op.size,
        ));
    }
    if x.size() == op.size {
        return x.clone();
    }
    LinearizedExpr::new(build_args_op_1(x.to_vec(), op.clone()))
}

pub fn simplify_slice(x: &LinearizedExpr, op: &LinearExpr, start: u8, end: u8) -> LinearizedExpr {
    assert_eq!(op.size as u8, end - start + 1);
    if x.is_constant() {
        let val = slice_val(x.get_constant_val(), start, end);
        return LinearizedExpr::from_linear_expr(LinearExpr::new(
            LinearExprOp::Const(val),
            op.size,
        ));
    }
    LinearizedExpr::new(build_args_op_1(x.to_vec(), op.clone()))
}

pub fn simplify_concat(x: &LinearizedExpr, y: &LinearizedExpr, op: &LinearExpr) -> LinearizedExpr {
    if x.is_constant() && y.is_constant() {
        let val = concat_val(x.get_constant_val(), y.get_constant_val(), x.size());
        return LinearizedExpr::from_linear_expr(LinearExpr::new(
            LinearExprOp::Const(val),
            op.size,
        ));
    }
    LinearizedExpr::new(build_args_op_2(x.to_vec(), y.to_vec(), op.clone()))
}

fn normalize<'e>(
    x: &'e LinearizedExpr,
    y: &'e LinearizedExpr,
) -> (&'e LinearizedExpr, &'e LinearizedExpr) {
    match (x.is_constant(), y.is_constant()) {
        _ if x.is_non_terminal() || y.is_non_terminal() => return (x, y),
        (false, true) => return (x, y),
        (true, false) => return (y, x),
        _ => return if x <= y { (x, y) } else { (y, x) },
    }
}

fn simplify_const_op_1<F>(x: &LinearizedExpr, f: F) -> LinearizedExpr
where
    F: Fn(u64) -> u64,
{
    let size = x.0.last().unwrap().size;
    let v1 = x.get_constant_val();
    let value = mask_to_size(f(mask_to_size(v1, size)), size);
    constant(value, size)
}

fn simplify_const_op_2<F>(x: &LinearizedExpr, y: &LinearizedExpr, f: F) -> LinearizedExpr
where
    F: Fn(u64, u64) -> u64,
{
    let size = x.0.last().unwrap().size;
    let v1 = x.get_constant_val();
    let v2 = y.get_constant_val();
    let value = mask_to_size(f(mask_to_size(v1, size), mask_to_size(v2, size)), size);
    constant(value, size)
}

pub fn simplify_cond(
    x: &LinearizedExpr,
    y: &LinearizedExpr,
    z: &LinearizedExpr,
    op: &LinearExpr,
) -> LinearizedExpr {
    if x.is_constant() {
        if x.get_constant_val() != 0 {
            return y.clone();
        } else {
            return z.clone();
        }
    }

    match op.op {
        // (_ ? x : x) => x
        _ if y == z && !y.is_non_terminal() => return y.clone(),
        _ => {}
    }
    no_simplification_op_3(x, y, z, op)
}
