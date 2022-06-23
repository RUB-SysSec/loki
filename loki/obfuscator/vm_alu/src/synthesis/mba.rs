use crate::config::CONFIG;
use crate::term_rewriting::term_rewriter::TermRewriter;
use intermediate_language::il::linearized_expressions::LinearizedExpr;

pub fn rewrite_to_equivalent_mba(
    expr_orig: LinearizedExpr,
    term_rewriter: &TermRewriter,
) -> LinearizedExpr {
    if !CONFIG.rewrite_mba || expr_orig.is_memory_op() {
        return expr_orig;
    }

    let expr = term_rewriter.rewrite_expr(expr_orig.clone());

    expr
}

pub fn rewrite_to_equivalent_mba_top_level(
    expr_orig: LinearizedExpr,
    term_rewriter: &TermRewriter,
) -> LinearizedExpr {
    if !CONFIG.rewrite_mba || expr_orig.is_memory_op() {
        return expr_orig;
    }

    let ret = term_rewriter.rewrite_top_level_expr(expr_orig);

    // println!("{} ---> {}\n", expr_orig.to_string(), ret.to_string());

    ret
}
