use il::linearized_expressions::*;
use utils::bit_vecs::mask_to_size;

pub fn op0(op: LinearExprOp, size: usize) -> LinearizedExpr {
    assert!(size > 0);
    LinearizedExpr::from_linear_expr(LinearExpr { op, size })
}

pub fn op1(x: LinearizedExpr, op: LinearExprOp, size: usize) -> LinearizedExpr {
    assert!(size > 0);
    let mut ret = LinearizedExpr::new(vec![]);
    ret.extend(x);
    ret.push(LinearExpr::new(op, size));
    ret
}

pub fn op2(x: LinearizedExpr, y: LinearizedExpr, op: LinearExprOp, size: usize) -> LinearizedExpr {
    assert!(size > 0);
    match op {
        LinearExprOp::Concat => {}
        LinearExprOp::Store => {}
        _ => {
            assert_eq!(x.size(), y.size());
            assert_eq!(x.size(), size);
        }
    }
    let mut ret = LinearizedExpr::new(vec![]);
    ret.extend(x);
    ret.extend(y);
    ret.push(LinearExpr::new(op, size));
    ret
}

pub fn op3(
    x: LinearizedExpr,
    y: LinearizedExpr,
    z: LinearizedExpr,
    op: LinearExprOp,
    size: usize,
) -> LinearizedExpr {
    assert!(size > 0);
    let mut ret = LinearizedExpr::new(vec![]);
    ret.extend(x);
    ret.extend(y);
    ret.extend(z);
    ret.push(LinearExpr::new(op, size));
    ret
}

pub fn assignment(lhs: LinearizedExpr, rhs: LinearizedExpr) -> LinearizedExpr {
    assert_eq!(lhs.size(), rhs.size());
    let assign = LinearExpr::new(LinearExprOp::Assign, lhs.size());
    let mut ret = LinearizedExpr::new(vec![]);
    ret.extend(lhs);
    ret.extend(rhs);
    ret.push(assign);
    ret
}

pub fn reg(s: &str, size: usize) -> LinearizedExpr {
    op0(LinearExprOp::Reg(String::from(s)), size)
}

pub fn reg_slice(start: u8, end: u8, size: usize) -> LinearizedExpr {
    op0(LinearExprOp::RegSlice(start, end), size)
}

pub fn reg_slice8(start: u8, end: u8) -> LinearizedExpr {
    reg_slice(start, end, 8)
}

pub fn reg_slice16(start: u8, end: u8) -> LinearizedExpr {
    reg_slice(start, end, 16)
}

pub fn reg_slice32(start: u8, end: u8) -> LinearizedExpr {
    reg_slice(start, end, 32)
}

pub fn reg_slice64(start: u8, end: u8) -> LinearizedExpr {
    reg_slice(start, end, 64)
}

pub fn const_slice(start: u8, end: u8, size: usize) -> LinearizedExpr {
    op0(LinearExprOp::ConstSlice(start, end), size)
}

pub fn const_slice5(start: u8, end: u8) -> LinearizedExpr {
    const_slice(start, end, 5)
}

pub fn const_slice8(start: u8, end: u8) -> LinearizedExpr {
    const_slice(start, end, 8)
}

pub fn const_slice16(start: u8, end: u8) -> LinearizedExpr {
    const_slice(start, end, 16)
}

pub fn const_slice26(start: u8, end: u8) -> LinearizedExpr {
    const_slice(start, end, 26)
}

pub fn const_slice32(start: u8, end: u8) -> LinearizedExpr {
    const_slice(start, end, 32)
}

pub fn const_slice64(start: u8, end: u8) -> LinearizedExpr {
    const_slice(start, end, 64)
}

pub fn constant(x: u64, size: usize) -> LinearizedExpr {
    op0(LinearExprOp::Const(mask_to_size(x, size)), size)
}

pub fn constant8(x: u64) -> LinearizedExpr {
    constant(x, 8)
}

pub fn constant16(x: u64) -> LinearizedExpr {
    constant(x, 16)
}

pub fn constant32(x: u64) -> LinearizedExpr {
    constant(x, 32)
}

pub fn constant64(x: u64) -> LinearizedExpr {
    constant(x, 64)
}

pub fn mem(x: LinearizedExpr, size: usize) -> LinearizedExpr {
    op1(x, LinearExprOp::Mem, size)
}

pub fn mem8(x: LinearizedExpr) -> LinearizedExpr {
    mem(x, 8)
}

pub fn mem16(x: LinearizedExpr) -> LinearizedExpr {
    mem(x, 16)
}

pub fn mem32(x: LinearizedExpr) -> LinearizedExpr {
    mem(x, 32)
}

pub fn load(x: LinearizedExpr, size: usize) -> LinearizedExpr {
    op1(x, LinearExprOp::Load, size)
}

pub fn store(x: LinearizedExpr, y: LinearizedExpr, size: usize) -> LinearizedExpr {
    op2(x, y, LinearExprOp::Store, size)
}

pub fn semantics_slice(
    x: LinearizedExpr,
    start: LinearizedExpr,
    end: LinearizedExpr,
    size: usize,
) -> LinearizedExpr {
    let shift = add(sub(end, start.clone(), size), constant(1, size), size);
    let mask = sub(
        shl_plain(constant(1, size), shift, size),
        constant(1, size),
        size,
    );

    and(mask, lshr_plain(x, start, size), size)
}

pub fn check_if_zero(x: LinearizedExpr, size: usize) -> LinearizedExpr {
    /* if 0 => 1 else 0*/
    add(
        not(
            ashr(
                and(
                    not(x.clone(), size),
                    sub(x.clone(), constant(1, size), size),
                    size,
                ),
                constant(63, size),
                size,
            ),
            size,
        ),
        constant(1, size),
        size,
    )
}

pub fn alloc(c: u64, size: usize) -> LinearizedExpr {
    op0(LinearExprOp::Alloc(mask_to_size(c, size)), size)
}

pub fn nop(size: usize) -> LinearizedExpr {
    op0(LinearExprOp::Nop, size)
}

pub fn not(x: LinearizedExpr, size: usize) -> LinearizedExpr {
    op1(x, LinearExprOp::Not, size)
}

pub fn not8(x: LinearizedExpr) -> LinearizedExpr {
    not(x, 8)
}

pub fn not16(x: LinearizedExpr) -> LinearizedExpr {
    not(x, 16)
}

pub fn not32(x: LinearizedExpr) -> LinearizedExpr {
    not(x, 32)
}

pub fn not64(x: LinearizedExpr) -> LinearizedExpr {
    not(x, 64)
}

pub fn neg(x: LinearizedExpr, size: usize) -> LinearizedExpr {
    op1(x, LinearExprOp::Neg, size)
}

pub fn neg8(x: LinearizedExpr) -> LinearizedExpr {
    neg(x, 8)
}

pub fn neg16(x: LinearizedExpr) -> LinearizedExpr {
    neg(x, 16)
}

pub fn neg32(x: LinearizedExpr) -> LinearizedExpr {
    neg(x, 32)
}

pub fn neg64(x: LinearizedExpr) -> LinearizedExpr {
    neg(x, 64)
}

pub fn sign_extend(x: LinearizedExpr, size: usize) -> LinearizedExpr {
    assert!(x.size() <= size);
    op1(x, LinearExprOp::SignExtend, size)
}

pub fn zero_extend(x: LinearizedExpr, size: usize) -> LinearizedExpr {
    assert!(x.size() <= size);
    op1(x, LinearExprOp::ZeroExtend, size)
}

pub fn slice(x: LinearizedExpr, start: u8, end: u8) -> LinearizedExpr {
    assert!(start <= end);
    let size = (end - start + 1) as usize;
    op1(x, LinearExprOp::Slice(start, end), size)
}

pub fn lsb(x: LinearizedExpr) -> LinearizedExpr {
    slice(x, 0, 0)
}

pub fn semantic_downcast(expr: LinearizedExpr, size: usize) -> LinearizedExpr {
    assert!(size <= 64);
    let expr_size = expr.size();
    match size {
        64 => expr,
        1 | 8 | 16 | 32 => and(expr, constant((1 << size as u64) - 1, expr_size), expr_size),
        _ => unreachable!(),
    }
}

pub fn semantic_sign_extension(expr: LinearizedExpr, size: usize) -> LinearizedExpr {
    let expr_size = expr.size();
    let mask = constant(1 << (expr_size - 1) as u64, expr_size);
    sub(
        zero_extend(xor(expr, mask.clone(), expr_size), size),
        zero_extend(mask, size),
        size,
    )
}

pub fn concat(x: LinearizedExpr, y: LinearizedExpr) -> LinearizedExpr {
    let size = x.size() + y.size();
    op2(x, y, LinearExprOp::Concat, size)
}

pub fn add(x: LinearizedExpr, y: LinearizedExpr, size: usize) -> LinearizedExpr {
    op2(x, y, LinearExprOp::Add, size)
}

pub fn add8(x: LinearizedExpr, y: LinearizedExpr) -> LinearizedExpr {
    add(x, y, 8)
}

pub fn add16(x: LinearizedExpr, y: LinearizedExpr) -> LinearizedExpr {
    add(x, y, 16)
}

pub fn add32(x: LinearizedExpr, y: LinearizedExpr) -> LinearizedExpr {
    add(x, y, 32)
}

pub fn add64(x: LinearizedExpr, y: LinearizedExpr) -> LinearizedExpr {
    add(x, y, 64)
}

pub fn mul(x: LinearizedExpr, y: LinearizedExpr, size: usize) -> LinearizedExpr {
    op2(x, y, LinearExprOp::Mul, size)
}

pub fn mul8(x: LinearizedExpr, y: LinearizedExpr) -> LinearizedExpr {
    mul(x, y, 8)
}

pub fn mul16(x: LinearizedExpr, y: LinearizedExpr) -> LinearizedExpr {
    mul(x, y, 16)
}

pub fn mul32(x: LinearizedExpr, y: LinearizedExpr) -> LinearizedExpr {
    mul(x, y, 32)
}

pub fn mul64(x: LinearizedExpr, y: LinearizedExpr) -> LinearizedExpr {
    mul(x, y, 64)
}

pub fn udiv(x: LinearizedExpr, y: LinearizedExpr, size: usize) -> LinearizedExpr {
    op2(x, y, LinearExprOp::Udiv, size)
}

pub fn udiv8(x: LinearizedExpr, y: LinearizedExpr) -> LinearizedExpr {
    udiv(x, y, 8)
}

pub fn udiv16(x: LinearizedExpr, y: LinearizedExpr) -> LinearizedExpr {
    udiv(x, y, 16)
}

pub fn udiv32(x: LinearizedExpr, y: LinearizedExpr) -> LinearizedExpr {
    udiv(x, y, 32)
}

pub fn udiv64(x: LinearizedExpr, y: LinearizedExpr) -> LinearizedExpr {
    udiv(x, y, 64)
}

pub fn sdiv(x: LinearizedExpr, y: LinearizedExpr, size: usize) -> LinearizedExpr {
    op2(x, y, LinearExprOp::Sdiv, size)
}

pub fn sdiv8(x: LinearizedExpr, y: LinearizedExpr) -> LinearizedExpr {
    sdiv(x, y, 8)
}

pub fn sdiv16(x: LinearizedExpr, y: LinearizedExpr) -> LinearizedExpr {
    sdiv(x, y, 16)
}

pub fn sdiv32(x: LinearizedExpr, y: LinearizedExpr) -> LinearizedExpr {
    sdiv(x, y, 32)
}

pub fn sdiv64(x: LinearizedExpr, y: LinearizedExpr) -> LinearizedExpr {
    sdiv(x, y, 64)
}

pub fn urem(x: LinearizedExpr, y: LinearizedExpr, size: usize) -> LinearizedExpr {
    op2(x, y, LinearExprOp::Urem, size)
}

pub fn urem8(x: LinearizedExpr, y: LinearizedExpr) -> LinearizedExpr {
    urem(x, y, 8)
}

pub fn urem16(x: LinearizedExpr, y: LinearizedExpr) -> LinearizedExpr {
    urem(x, y, 16)
}

pub fn urem32(x: LinearizedExpr, y: LinearizedExpr) -> LinearizedExpr {
    urem(x, y, 32)
}

pub fn urem64(x: LinearizedExpr, y: LinearizedExpr) -> LinearizedExpr {
    urem(x, y, 64)
}

pub fn srem(x: LinearizedExpr, y: LinearizedExpr, size: usize) -> LinearizedExpr {
    op2(x, y, LinearExprOp::Srem, size)
}

pub fn srem8(x: LinearizedExpr, y: LinearizedExpr) -> LinearizedExpr {
    srem(x, y, 8)
}

pub fn srem16(x: LinearizedExpr, y: LinearizedExpr) -> LinearizedExpr {
    srem(x, y, 16)
}

pub fn srem32(x: LinearizedExpr, y: LinearizedExpr) -> LinearizedExpr {
    srem(x, y, 32)
}

pub fn srem64(x: LinearizedExpr, y: LinearizedExpr) -> LinearizedExpr {
    srem(x, y, 64)
}

pub fn sub(x: LinearizedExpr, y: LinearizedExpr, size: usize) -> LinearizedExpr {
    op2(x, y, LinearExprOp::Sub, size)
}

pub fn sub8(x: LinearizedExpr, y: LinearizedExpr) -> LinearizedExpr {
    sub(x, y, 8)
}

pub fn sub16(x: LinearizedExpr, y: LinearizedExpr) -> LinearizedExpr {
    sub(x, y, 16)
}

pub fn sub32(x: LinearizedExpr, y: LinearizedExpr) -> LinearizedExpr {
    sub(x, y, 32)
}

pub fn sub64(x: LinearizedExpr, y: LinearizedExpr) -> LinearizedExpr {
    sub(x, y, 64)
}

pub fn and(x: LinearizedExpr, y: LinearizedExpr, size: usize) -> LinearizedExpr {
    op2(x, y, LinearExprOp::And, size)
}

pub fn and8(x: LinearizedExpr, y: LinearizedExpr) -> LinearizedExpr {
    and(x, y, 8)
}

pub fn and16(x: LinearizedExpr, y: LinearizedExpr) -> LinearizedExpr {
    and(x, y, 16)
}

pub fn and32(x: LinearizedExpr, y: LinearizedExpr) -> LinearizedExpr {
    and(x, y, 32)
}

pub fn and64(x: LinearizedExpr, y: LinearizedExpr) -> LinearizedExpr {
    and(x, y, 64)
}

pub fn or(x: LinearizedExpr, y: LinearizedExpr, size: usize) -> LinearizedExpr {
    op2(x, y, LinearExprOp::Or, size)
}

pub fn or8(x: LinearizedExpr, y: LinearizedExpr) -> LinearizedExpr {
    or(x, y, 8)
}

pub fn or16(x: LinearizedExpr, y: LinearizedExpr) -> LinearizedExpr {
    or(x, y, 16)
}

pub fn or32(x: LinearizedExpr, y: LinearizedExpr) -> LinearizedExpr {
    or(x, y, 32)
}

pub fn or64(x: LinearizedExpr, y: LinearizedExpr) -> LinearizedExpr {
    or(x, y, 64)
}

pub fn xor(x: LinearizedExpr, y: LinearizedExpr, size: usize) -> LinearizedExpr {
    op2(x, y, LinearExprOp::Xor, size)
}

pub fn xor8(x: LinearizedExpr, y: LinearizedExpr) -> LinearizedExpr {
    xor(x, y, 8)
}

pub fn xor16(x: LinearizedExpr, y: LinearizedExpr) -> LinearizedExpr {
    xor(x, y, 16)
}

pub fn xor32(x: LinearizedExpr, y: LinearizedExpr) -> LinearizedExpr {
    xor(x, y, 32)
}

pub fn xor64(x: LinearizedExpr, y: LinearizedExpr) -> LinearizedExpr {
    xor(x, y, 64)
}

pub fn nand(x: LinearizedExpr, y: LinearizedExpr, size: usize) -> LinearizedExpr {
    op2(x, y, LinearExprOp::Nand, size)
}

pub fn nand8(x: LinearizedExpr, y: LinearizedExpr) -> LinearizedExpr {
    nand(x, y, 8)
}

pub fn nand16(x: LinearizedExpr, y: LinearizedExpr) -> LinearizedExpr {
    nand(x, y, 16)
}

pub fn nand32(x: LinearizedExpr, y: LinearizedExpr) -> LinearizedExpr {
    nand(x, y, 32)
}

pub fn nand64(x: LinearizedExpr, y: LinearizedExpr) -> LinearizedExpr {
    nand(x, y, 64)
}

pub fn nor(x: LinearizedExpr, y: LinearizedExpr, size: usize) -> LinearizedExpr {
    op2(x, y, LinearExprOp::Nor, size)
}

pub fn nor8(x: LinearizedExpr, y: LinearizedExpr) -> LinearizedExpr {
    nor(x, y, 8)
}

pub fn nor16(x: LinearizedExpr, y: LinearizedExpr) -> LinearizedExpr {
    nor(x, y, 16)
}

pub fn nor32(x: LinearizedExpr, y: LinearizedExpr) -> LinearizedExpr {
    nor(x, y, 32)
}

pub fn nor64(x: LinearizedExpr, y: LinearizedExpr) -> LinearizedExpr {
    nor(x, y, 64)
}

pub fn ult(x: LinearizedExpr, y: LinearizedExpr, size: usize) -> LinearizedExpr {
    op2(x, y, LinearExprOp::Ult, size)
}

pub fn ult8(x: LinearizedExpr, y: LinearizedExpr) -> LinearizedExpr {
    ult(x, y, 8)
}

pub fn ult16(x: LinearizedExpr, y: LinearizedExpr) -> LinearizedExpr {
    ult(x, y, 16)
}

pub fn ult32(x: LinearizedExpr, y: LinearizedExpr) -> LinearizedExpr {
    ult(x, y, 32)
}

pub fn ult64(x: LinearizedExpr, y: LinearizedExpr) -> LinearizedExpr {
    ult(x, y, 64)
}

pub fn slt(x: LinearizedExpr, y: LinearizedExpr, size: usize) -> LinearizedExpr {
    op2(x, y, LinearExprOp::Slt, size)
}

pub fn slt8(x: LinearizedExpr, y: LinearizedExpr) -> LinearizedExpr {
    slt(x, y, 8)
}

pub fn slt16(x: LinearizedExpr, y: LinearizedExpr) -> LinearizedExpr {
    slt(x, y, 16)
}

pub fn slt32(x: LinearizedExpr, y: LinearizedExpr) -> LinearizedExpr {
    slt(x, y, 32)
}

pub fn slt64(x: LinearizedExpr, y: LinearizedExpr) -> LinearizedExpr {
    slt(x, y, 64)
}

pub fn ule(x: LinearizedExpr, y: LinearizedExpr, size: usize) -> LinearizedExpr {
    op2(x, y, LinearExprOp::Ule, size)
}

pub fn ule8(x: LinearizedExpr, y: LinearizedExpr) -> LinearizedExpr {
    ule(x, y, 8)
}

pub fn ule16(x: LinearizedExpr, y: LinearizedExpr) -> LinearizedExpr {
    ule(x, y, 16)
}

pub fn ule32(x: LinearizedExpr, y: LinearizedExpr) -> LinearizedExpr {
    ule(x, y, 32)
}

pub fn ule64(x: LinearizedExpr, y: LinearizedExpr) -> LinearizedExpr {
    ule(x, y, 64)
}

pub fn sle(x: LinearizedExpr, y: LinearizedExpr, size: usize) -> LinearizedExpr {
    op2(x, y, LinearExprOp::Sle, size)
}

pub fn sle8(x: LinearizedExpr, y: LinearizedExpr) -> LinearizedExpr {
    sle(x, y, 8)
}

pub fn sle16(x: LinearizedExpr, y: LinearizedExpr) -> LinearizedExpr {
    sle(x, y, 16)
}

pub fn sle32(x: LinearizedExpr, y: LinearizedExpr) -> LinearizedExpr {
    sle(x, y, 32)
}

pub fn sle64(x: LinearizedExpr, y: LinearizedExpr) -> LinearizedExpr {
    sle(x, y, 64)
}

pub fn ugt(x: LinearizedExpr, y: LinearizedExpr, size: usize) -> LinearizedExpr {
    op2(y, x, LinearExprOp::Ult, size)
}

pub fn ugt8(x: LinearizedExpr, y: LinearizedExpr) -> LinearizedExpr {
    ugt(x, y, 8)
}

pub fn ugt16(x: LinearizedExpr, y: LinearizedExpr) -> LinearizedExpr {
    ugt(x, y, 16)
}

pub fn ugt32(x: LinearizedExpr, y: LinearizedExpr) -> LinearizedExpr {
    ugt(x, y, 32)
}

pub fn ugt64(x: LinearizedExpr, y: LinearizedExpr) -> LinearizedExpr {
    ugt(x, y, 64)
}

pub fn sgt(x: LinearizedExpr, y: LinearizedExpr, size: usize) -> LinearizedExpr {
    op2(y, x, LinearExprOp::Slt, size)
}

pub fn sgt8(x: LinearizedExpr, y: LinearizedExpr) -> LinearizedExpr {
    sgt(x, y, 8)
}

pub fn sgt16(x: LinearizedExpr, y: LinearizedExpr) -> LinearizedExpr {
    sgt(x, y, 16)
}

pub fn sgt32(x: LinearizedExpr, y: LinearizedExpr) -> LinearizedExpr {
    sgt(x, y, 32)
}

pub fn sgt64(x: LinearizedExpr, y: LinearizedExpr) -> LinearizedExpr {
    sgt(x, y, 64)
}

pub fn uge(x: LinearizedExpr, y: LinearizedExpr, size: usize) -> LinearizedExpr {
    ule(y, x, size)
}

pub fn uge8(x: LinearizedExpr, y: LinearizedExpr) -> LinearizedExpr {
    uge(x, y, 8)
}

pub fn uge16(x: LinearizedExpr, y: LinearizedExpr) -> LinearizedExpr {
    uge(x, y, 16)
}

pub fn uge32(x: LinearizedExpr, y: LinearizedExpr) -> LinearizedExpr {
    uge(x, y, 32)
}

pub fn uge64(x: LinearizedExpr, y: LinearizedExpr) -> LinearizedExpr {
    uge(x, y, 64)
}

pub fn sge(x: LinearizedExpr, y: LinearizedExpr, size: usize) -> LinearizedExpr {
    sle(y, x, size)
}

pub fn sge8(x: LinearizedExpr, y: LinearizedExpr) -> LinearizedExpr {
    sge(x, y, 8)
}

pub fn sge16(x: LinearizedExpr, y: LinearizedExpr) -> LinearizedExpr {
    sge(x, y, 16)
}

pub fn sge32(x: LinearizedExpr, y: LinearizedExpr) -> LinearizedExpr {
    sge(x, y, 32)
}

pub fn sge64(x: LinearizedExpr, y: LinearizedExpr) -> LinearizedExpr {
    sge(x, y, 64)
}

pub fn equal(x: LinearizedExpr, y: LinearizedExpr, size: usize) -> LinearizedExpr {
    op2(x, y, LinearExprOp::Equal, size)
}

pub fn equal8(x: LinearizedExpr, y: LinearizedExpr) -> LinearizedExpr {
    equal(x, y, 8)
}

pub fn equal16(x: LinearizedExpr, y: LinearizedExpr) -> LinearizedExpr {
    equal(x, y, 16)
}

pub fn equal32(x: LinearizedExpr, y: LinearizedExpr) -> LinearizedExpr {
    equal(x, y, 32)
}

pub fn equal64(x: LinearizedExpr, y: LinearizedExpr) -> LinearizedExpr {
    equal(x, y, 64)
}

fn reduce_shift_op(y: LinearizedExpr, size: usize) -> LinearizedExpr {
    let shift_size = match size {
        64 => 63,
        _ => 31,
    };
    and(y, constant(shift_size, size), size)
}

pub fn shl(x: LinearizedExpr, y: LinearizedExpr, size: usize) -> LinearizedExpr {
    let y = reduce_shift_op(y, size);
    op2(x, y, LinearExprOp::Shl, size)
}

pub fn shl8(x: LinearizedExpr, y: LinearizedExpr) -> LinearizedExpr {
    shl(x, y, 8)
}

pub fn shl16(x: LinearizedExpr, y: LinearizedExpr) -> LinearizedExpr {
    shl(x, y, 16)
}

pub fn shl32(x: LinearizedExpr, y: LinearizedExpr) -> LinearizedExpr {
    shl(x, y, 32)
}

pub fn shl64(x: LinearizedExpr, y: LinearizedExpr) -> LinearizedExpr {
    shl(x, y, 64)
}

pub fn shl_plain(x: LinearizedExpr, y: LinearizedExpr, size: usize) -> LinearizedExpr {
    op2(x, y, LinearExprOp::Shl, size)
}

pub fn shl8_plain(x: LinearizedExpr, y: LinearizedExpr) -> LinearizedExpr {
    shl_plain(x, y, 8)
}

pub fn shl16_plain(x: LinearizedExpr, y: LinearizedExpr) -> LinearizedExpr {
    shl_plain(x, y, 16)
}

pub fn shl32_plain(x: LinearizedExpr, y: LinearizedExpr) -> LinearizedExpr {
    shl_plain(x, y, 32)
}

pub fn shl64_plain(x: LinearizedExpr, y: LinearizedExpr) -> LinearizedExpr {
    shl_plain(x, y, 64)
}

pub fn lshr(x: LinearizedExpr, y: LinearizedExpr, size: usize) -> LinearizedExpr {
    let y = reduce_shift_op(y, size);
    op2(x, y, LinearExprOp::Lshr, size)
}

pub fn lshr8(x: LinearizedExpr, y: LinearizedExpr) -> LinearizedExpr {
    lshr(x, y, 8)
}

pub fn lshr16(x: LinearizedExpr, y: LinearizedExpr) -> LinearizedExpr {
    lshr(x, y, 16)
}

pub fn lshr32(x: LinearizedExpr, y: LinearizedExpr) -> LinearizedExpr {
    lshr(x, y, 32)
}

pub fn lshr64(x: LinearizedExpr, y: LinearizedExpr) -> LinearizedExpr {
    lshr(x, y, 64)
}

pub fn lshr_plain(x: LinearizedExpr, y: LinearizedExpr, size: usize) -> LinearizedExpr {
    op2(x, y, LinearExprOp::Lshr, size)
}

pub fn lshr8_plain(x: LinearizedExpr, y: LinearizedExpr) -> LinearizedExpr {
    lshr_plain(x, y, 8)
}

pub fn lshr16_plain(x: LinearizedExpr, y: LinearizedExpr) -> LinearizedExpr {
    lshr_plain(x, y, 16)
}

pub fn lshr32_plain(x: LinearizedExpr, y: LinearizedExpr) -> LinearizedExpr {
    lshr_plain(x, y, 32)
}

pub fn lshr64_plain(x: LinearizedExpr, y: LinearizedExpr) -> LinearizedExpr {
    lshr_plain(x, y, 64)
}

pub fn ashr(x: LinearizedExpr, y: LinearizedExpr, size: usize) -> LinearizedExpr {
    let y = reduce_shift_op(y, size);
    op2(x, y, LinearExprOp::Ashr, size)
}

pub fn ashr8(x: LinearizedExpr, y: LinearizedExpr) -> LinearizedExpr {
    ashr(x, y, 8)
}

pub fn ashr16(x: LinearizedExpr, y: LinearizedExpr) -> LinearizedExpr {
    ashr(x, y, 16)
}

pub fn ashr32(x: LinearizedExpr, y: LinearizedExpr) -> LinearizedExpr {
    ashr(x, y, 32)
}

pub fn ashr64(x: LinearizedExpr, y: LinearizedExpr) -> LinearizedExpr {
    ashr(x, y, 64)
}

pub fn ashr_plain(x: LinearizedExpr, y: LinearizedExpr, size: usize) -> LinearizedExpr {
    op2(x, y, LinearExprOp::Ashr, size)
}

pub fn ashr8_plain(x: LinearizedExpr, y: LinearizedExpr) -> LinearizedExpr {
    ashr_plain(x, y, 8)
}

pub fn ashr16_plain(x: LinearizedExpr, y: LinearizedExpr) -> LinearizedExpr {
    ashr_plain(x, y, 16)
}

pub fn ashr32_plain(x: LinearizedExpr, y: LinearizedExpr) -> LinearizedExpr {
    ashr_plain(x, y, 32)
}

pub fn ashr64_plain(x: LinearizedExpr, y: LinearizedExpr) -> LinearizedExpr {
    ashr_plain(x, y, 64)
}

pub fn ite(x: LinearizedExpr, y: LinearizedExpr, z: LinearizedExpr, size: usize) -> LinearizedExpr {
    assert_eq!(y.size(), z.size(), "y != z");
    assert_eq!(size, z.size(), "size != z");
    op3(x, y, z, LinearExprOp::Ite, size)
}

pub fn ite8(x: LinearizedExpr, y: LinearizedExpr, z: LinearizedExpr) -> LinearizedExpr {
    ite(x, y, z, 8)
}

pub fn ite16(x: LinearizedExpr, y: LinearizedExpr, z: LinearizedExpr) -> LinearizedExpr {
    ite(x, y, z, 16)
}

pub fn ite32(x: LinearizedExpr, y: LinearizedExpr, z: LinearizedExpr) -> LinearizedExpr {
    ite(x, y, z, 32)
}

pub fn ite64(x: LinearizedExpr, y: LinearizedExpr, z: LinearizedExpr) -> LinearizedExpr {
    ite(x, y, z, 64)
}

pub fn semantics_ite(x: LinearizedExpr, y: LinearizedExpr, z: LinearizedExpr) -> LinearizedExpr {
    let size = z.size();
    let cond = semantic_downcast(
        not(
            semantic_downcast(equal(x.clone(), constant(0, x.size()), x.size()), 1),
            x.size(),
        ),
        1,
    );
    add(
        mul(zero_extend(cond.clone(), y.size()), y, size),
        mul(
            zero_extend(
                semantic_downcast(not(cond.clone(), cond.size()), 1),
                z.size(),
            ),
            z,
            size,
        ),
        size,
    )
}
