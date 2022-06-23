use crate::bytecode::keys::ALUKeys;
use crate::synthesis::mba::{rewrite_to_equivalent_mba, rewrite_to_equivalent_mba_top_level};
use crate::term_rewriting::term_rewriter::TermRewriter;
use intermediate_language::il::expression_utils::*;
use intermediate_language::il::linearized_expressions::LinearizedExpr;
use intermediate_language::utils::bit_vecs::slice_val;
use primal_check::miller_rabin;
use rand::thread_rng;
use rand::Rng;
use rayon::prelude::*;

fn is_prime(n: u64) -> bool {
    miller_rabin(n)
}

fn gen_prime_candidate(size: u64) -> u64 {
    let mut canditate = thread_rng().gen::<u64>() & ((1 << size) - 1);
    canditate |= 1;
    canditate
}

fn gen_rand_prime(size: u64) -> u64 {
    let mut candiate = gen_prime_candidate(size);
    while !is_prime(candiate) || candiate < (1 << 29) {
        candiate = gen_prime_candidate(size);
    }

    candiate
}

fn gen_semiprime(keys: &ALUKeys, index: usize) -> u64 {
    let p1 = keys.get(index);
    let p2 = keys.get_additional_key(index);

    p1 * p2
}

pub fn constraint_key_with_primes(
    keys: &ALUKeys,
    index: usize,
    term_rewriter: &TermRewriter,
) -> LinearizedExpr {
    rewrite_to_equivalent_mba(
        check_if_zero(
            urem64(
                constant64(gen_semiprime(keys, index)),
                and64(reg("k", 64), constant64((1 << 32) - 1)),
            ),
            64,
        ),
        term_rewriter,
    )
}

fn key_slice(key: u64, start: u64, end: u64) -> LinearizedExpr {
    check_if_zero(
        sub64(
            semantics_slice(reg("k", 64), constant64(start), constant64(end), 64),
            constant64(slice_val(key, start as u8, end as u8)),
        ),
        64,
    )
    .simplify()
}

fn constraint_key_with_multiple_roots(
    keys: &ALUKeys,
    index: usize,
    term_rewriter: &TermRewriter,
) -> LinearizedExpr {
    let key: u64 = keys.get(index);

    /* how many subkeys to check */
    let num: u64 = match thread_rng().gen::<u64>() % 3 {
        0 => 2,
        1 => 4,
        2 => 8,
        _ => unreachable!(),
    };

    let mut start = 0;
    let mut end = (64 / num) - 1;
    let mut ret = key_slice(key, start, end);

    for index in 1..num {
        start = (64 / num) * index;
        end = (64 / num) * (index + 1) - 1;

        ret = mul64(ret, key_slice(key, start, end));
    }

    rewrite_to_equivalent_mba(ret, term_rewriter)
}

pub fn constraint_key_with_point_function(
    keys: &ALUKeys,
    index: usize,
    term_rewriter: &TermRewriter,
) -> LinearizedExpr {
    match synthesize_point_function(keys, index) {
        Some(expr) => rewrite_to_equivalent_mba(expr, term_rewriter),
        None => constraint_key_with_multiple_roots(keys, index, term_rewriter),
    }
}

pub fn synthesize_point_function(keys: &ALUKeys, set_index: usize) -> Option<LinearizedExpr> {
    /* trade-off between being successful and waiting to finish*/
    (0..2500)
        .into_par_iter()
        .map(|_| gen_expr())
        .find_any(|e| verify_constraints(&e, keys, set_index))
}

fn rand_var() -> LinearizedExpr {
    match thread_rng().gen::<usize>() % 9 {
        0 => semantics_slice(reg("k", 64), constant64(0), constant64(7), 64),
        1 => semantics_slice(reg("k", 64), constant64(8), constant64(15), 64),
        2 => semantics_slice(reg("k", 64), constant64(16), constant64(23), 64),
        3 => semantics_slice(reg("k", 64), constant64(24), constant64(31), 64),
        4 => semantics_slice(reg("k", 64), constant64(32), constant64(39), 64),
        5 => semantics_slice(reg("k", 64), constant64(40), constant64(47), 64),
        6 => semantics_slice(reg("k", 64), constant64(48), constant64(55), 64),
        7 => semantics_slice(reg("k", 64), constant64(56), constant64(63), 64),
        8 => constant(thread_rng().gen::<u64>(), 64),
        _ => unreachable!(),
    }
}

fn gen_expr() -> LinearizedExpr {
    let mut expr = rand_var();
    let size = 64;

    /*
        - generate at least layer 5 expression to be more successful
        - generate at max layer 15 expression to limit overhead
    */
    for _ in 0..thread_rng().gen::<usize>() % 10 + 5 {
        expr = match thread_rng().gen::<usize>() % 11 {
            0 => add(expr, rand_var(), size),
            1 => sub(expr, rand_var(), size),
            2 => mul(expr, rand_var(), size),
            3 => and(expr, rand_var(), size),
            4 => or(expr, rand_var(), size),
            5 => xor(expr, rand_var(), size),
            6 => nand(expr, rand_var(), size),
            7 => nor(expr, rand_var(), size),
            8 => not(expr, size),
            9 => neg(expr, size),
            10 => mul(expr.clone(), expr, size),
            _ => unreachable!(),
        };
    }

    expr.simplify()
}

fn verify_constraints(expr: &LinearizedExpr, keys: &ALUKeys, set_index: usize) -> bool {
    (0..keys.len()).into_iter().all(|index| {
        let mut e = expr.clone();
        e.replace_subexpr(&reg("k", 64), &constant(keys.get(index), 64));
        e.simplify().get_constant_val() == if index == set_index { 1 } else { 0 }
    }) && keys.iter_additional_keys().all(|v| {
        let mut e = expr.clone();
        e.replace_subexpr(&reg("k", 64), &constant(*v, 64));
        e.simplify().get_constant_val() == 0
    })
}

pub fn constraint_with_key(
    keys: &ALUKeys,
    index: usize,
    term_rewriter: &TermRewriter,
) -> LinearizedExpr {
    match keys.contains_additional_key(index) {
        true => constraint_key_with_primes(keys, index, term_rewriter),
        false => constraint_key_with_point_function(keys, index, term_rewriter),
    }
}

pub fn constraint_operation(
    instruction: LinearizedExpr,
    keys: &ALUKeys,
    index: usize,
    term_rewriter: &TermRewriter,
) -> LinearizedExpr {
    rewrite_to_equivalent_mba_top_level(
        mul64(constraint_with_key(keys, index, term_rewriter), instruction),
        term_rewriter,
    )
}

fn gen_rand_key(keys: &mut ALUKeys) {
    let prime: bool = thread_rng().gen();

    let mut key: u64 = match prime {
        true => gen_rand_prime(32),
        false => thread_rng().gen(),
    };

    while keys.contains(key) {
        key = match prime {
            true => gen_rand_prime(32),
            false => thread_rng().gen(),
        };
    }

    keys.push(key);

    if prime {
        let mut key: u64 = gen_rand_prime(32);
        while keys.contains(key) {
            key = gen_rand_prime(32);
        }
        keys.insert_additional_key(keys.len() - 1, key);
    }
}

pub fn thwart(
    instructions: &[LinearizedExpr],
    keys: &mut ALUKeys,
    term_rewriter: &TermRewriter,
) -> LinearizedExpr {
    instructions.iter().for_each(|_| gen_rand_key(keys));
    thwart_recursive(instructions, keys, 0, term_rewriter)
}

pub fn thwart_recursive(
    instructions: &[LinearizedExpr],
    keys: &ALUKeys,
    index: usize,
    term_rewriter: &TermRewriter,
) -> LinearizedExpr {
    match instructions.len() {
        2 => rewrite_to_equivalent_mba_top_level(
            add64(
                constraint_operation(instructions[0].clone(), keys, index, term_rewriter),
                constraint_operation(instructions[1].clone(), keys, index + 1, term_rewriter),
            ),
            term_rewriter,
        ),
        _ => add64(
            constraint_operation(instructions[0].clone(), keys, index, term_rewriter),
            thwart_recursive(&instructions[1..], keys, index + 1, term_rewriter),
        ),
    }
}
