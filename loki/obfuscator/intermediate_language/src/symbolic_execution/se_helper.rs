use il::linearized_expressions::{LinearExpr, LinearizedExpr};

pub fn build_op_1(x: &LinearizedExpr, op: &LinearExpr) -> LinearizedExpr {
    let args = build_args_op_1(x.to_vec(), op.clone());
    LinearizedExpr::new(args)
}

pub fn build_op_2(x: &LinearizedExpr, y: &LinearizedExpr, op: &LinearExpr) -> LinearizedExpr {
    let args = build_args_op_2(x.to_vec(), y.to_vec(), op.clone());
    LinearizedExpr::new(args)
}

pub fn build_args_op_1(x: Vec<LinearExpr>, expr: LinearExpr) -> Vec<LinearExpr> {
    let mut ret = vec![];
    ret.extend(x);
    ret.extend(vec![expr]);
    ret
}

pub fn build_args_op_2(
    x: Vec<LinearExpr>,
    y: Vec<LinearExpr>,
    expr: LinearExpr,
) -> Vec<LinearExpr> {
    let mut ret = vec![];
    ret.extend(x);
    ret.extend(y);
    ret.extend(vec![expr]);
    ret
}

pub fn build_args_op_3(
    x: Vec<LinearExpr>,
    y: Vec<LinearExpr>,
    z: Vec<LinearExpr>,
    expr: LinearExpr,
) -> Vec<LinearExpr> {
    let mut res = vec![];
    res.extend(x);
    res.extend(y);
    res.extend(z);
    res.extend(vec![expr]);
    res
}

pub fn build_args_op_n(v: Vec<Vec<LinearExpr>>, expr: LinearExpr) -> Vec<LinearExpr> {
    let mut res = vec![];
    for x in v.into_iter() {
        res.extend(x);
    }
    res.extend(vec![expr.clone()]);
    res
}

pub fn split_into_args(expr: &LinearizedExpr) -> Vec<LinearizedExpr> {
    let mut stack = vec![];
    for (index, e) in expr.0.iter().enumerate() {
        if index == expr.0.len() - 1 {
            return stack;
        }
        let n = e.arity();
        match n {
            0 => {
                stack.push(LinearizedExpr::from_linear_expr(e.clone()));
            }
            1 => {
                let x = stack.pop().unwrap();
                let mut res = LinearizedExpr::new(vec![]);
                res.extend(x);
                res.push(e.clone());
                stack.push(res);
            }
            2 => {
                let y = stack.pop().unwrap();
                let x = stack.pop().unwrap();
                let mut res = LinearizedExpr::new(vec![]);
                res.extend(x);
                res.extend(y);
                res.push(e.clone());
                stack.push(res);
            }
            3 => {
                let z = stack.pop().unwrap();
                let y = stack.pop().unwrap();
                let x = stack.pop().unwrap();
                let mut res = LinearizedExpr::new(vec![]);
                res.extend(x);
                res.extend(y);
                res.extend(z);
                res.push(e.clone());
                stack.push(res);
            }
            _ => unreachable!(),
        }
    }
    stack
}
