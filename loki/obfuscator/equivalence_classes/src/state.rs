use intermediate_language::il::expression_utils::*;
use intermediate_language::il::linearized_expressions::LinearizedExpr;

#[derive(Debug)]
pub struct State {
    op_index: usize,
    pub expr: LinearizedExpr,
    replacement_index: Option<usize>,
}

impl State {
    pub fn new(size: usize) -> State {
        State {
            op_index: 0,
            expr: reg("NT", size),
            replacement_index: Some(0),
        }
    }

    pub fn next_state(&mut self) -> State {
        assert!(self.remaining_moves());
        self.op_index += 1;
        let next_expr = self.next_expr();

        State {
            op_index: 0,
            replacement_index: first_non_terminal(&next_expr),
            expr: next_expr,
        }
    }

    fn next_expr(&self) -> LinearizedExpr {
        let mut next_expr = self.expr.clone();
        let extension = gen_expr(self.op_index - 1, self.expr.size());
        next_expr.replace_at_pos(self.replacement_index.unwrap(), &extension);
        next_expr
    }

    pub fn remaining_moves(&self) -> bool {
        self.replacement_index.is_some() && self.op_index < 16
    }

    pub fn is_terminal(&self) -> bool {
        self.expr
            .0
            .iter()
            .filter(|e| e.is_var())
            .all(|e| e.get_var_name() != "NT")
    }

    pub fn is_normalized(&self) -> bool {
        self.expr == self.expr.simplify()
    }

    pub fn to_string(&self) -> String {
        self.expr.to_infix()
    }
}

fn get_non_terminal_var_indices(expr: &LinearizedExpr) -> Vec<usize> {
    expr.0
        .iter()
        .enumerate()
        .filter(|(_, e)| e.is_var() && e.get_var_name() == "NT")
        .map(|(index, _)| index)
        .collect()
}

fn first_non_terminal(expr: &LinearizedExpr) -> Option<usize> {
    match get_non_terminal_var_indices(expr).get(0) {
        Some(x) => Some(*x),
        None => None,
    }
}

pub fn gen_expr(index: usize, size: usize) -> LinearizedExpr {
    /* non-terminal variables*/
    let x = reg("NT", size);
    let y = reg("NT", size);
    let _z = reg("NT", size);

    match index {
        0 => add(x, y, size),
        1 => sub(x, y, size),
        2 => or(x, y, size),
        3 => and(x, y, size),
        4 => xor(x, y, size),
        5 => nand(x, y, size),
        6 => nor(x, y, size),
        7 => not(x, size),
        8 => neg(x, size),
        9 => shl(x, y, size),
        10 => mul(x, y, size),
        11 => reg("p0", size),
        12 => reg("p1", size),
        13 => constant(0, size),
        14 => constant(1, size),
        15 => constant(2, size),
        _ => unreachable!(),
    }
}
