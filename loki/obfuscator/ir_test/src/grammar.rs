use intermediate_language::il::expression_utils::*;
use intermediate_language::il::linearized_expressions::LinearizedExpr;
use rand::seq::SliceRandom;
use rand::thread_rng;
use rand::Rng;

fn get_non_terminal_var_indices(expr: &LinearizedExpr) -> Vec<usize> {
    expr.0
        .iter()
        .enumerate()
        .filter(|(_, e)| e.is_var() && e.get_var_name() == "NT")
        .map(|(index, _)| index)
        .collect()
}

pub fn gen_var(num: usize, size: usize) -> LinearizedExpr {
    let name = format!("R{}", num);
    reg(&name, size)
}

fn rand_var(num_vars: usize, size: usize) -> LinearizedExpr {
    assert!(num_vars > 1);
    let coin = thread_rng().gen::<usize>() % 3;
    match coin {
        0 => {
            let num = thread_rng().gen::<usize>() % num_vars;
            gen_var(num, size)
        }
        1 => constant(0, size),
        2 => constant(1, size),
        _ => unreachable!(),
    }
}

pub fn gen_expr_with_depth(num_vars: usize, n: usize, size: usize) -> LinearizedExpr {
    /* random expression init */
    let mut expr = gen_expr(size);

    /* extend expression */
    for _ in 0..n {
        /* locate all non-terminal var indices in expression */
        let indices: Vec<_> = get_non_terminal_var_indices(&expr);

        /* choose random index */
        let rand_index = *indices.choose(&mut thread_rng()).unwrap();

        /* choose random expression */
        let rand_expr = gen_expr(size);

        /* replace subexpression with random new expression */
        expr.replace_at_pos(rand_index, &rand_expr);
    }

    /* locate all non-terminal var indices in expression */
    let indices = get_non_terminal_var_indices(&expr);

    /* replace all non-terminal variables with random terminal variables */
    for index in indices {
        expr.replace_at_pos(index, &rand_var(num_vars, size));
    }

    expr
}

pub fn gen_expr(size: usize) -> LinearizedExpr {
    /* non-terminal variables*/
    let x = reg("NT", size);
    let y = reg("NT", size);

    let coin = thread_rng().gen::<usize>() % 21; // 25

    match coin {
        0 => add(x, y, size),
        1 => sub(x, y, size),
        2 => mul(x, y, size),
        3 => udiv(x, y, size),
        4 => sdiv(x, y, size),
        5 => urem(x, y, size),
        6 => srem(x, y, size),
        7 => shl_plain(x, y, size),
        8 => lshr_plain(x, y, size),
        9 => ashr_plain(x, y, size),
        10 => and(x, y, size),
        11 => or(x, y, size),
        12 => xor(x, y, size),
        13 => nand(x, y, size),
        14 => nor(x, y, size),
        15 => not(x, size),
        16 => neg(x, size),
        17 => ult(x.clone(), y.clone(), size),
        18 => slt(x.clone(), y.clone(), size),
        19 => ule(x.clone(), y.clone(), size),
        20 => sle(x.clone(), y.clone(), size),
        21 => zero_extend(x, size * 2),
        22 => sign_extend(x, size * 2),
        23 => slice(x, 0, 7),
        24 => concat(x, y),
        _ => unreachable!(),
    }
}
