use crate::config::CONFIG;
use equivalence_classes::semantics_map::SemanticsMap;
use intermediate_language::il::expression_utils::*;
use intermediate_language::il::linearized_expressions::{LinearExpr, LinearExprOp, LinearizedExpr};
use intermediate_language::FastHashMap;
use rand::prelude::*;
use rand::seq::SliceRandom;
use rand::thread_rng;

pub struct TermRewriter {
    rules_map: FastHashMap<LinearExpr, Vec<LinearizedExpr>>,
}

impl TermRewriter {
    pub fn new() -> TermRewriter {
        let semantics_map = match CONFIG.rewrite_mba {
            true => SemanticsMap::unify_from_files(&CONFIG.equivalence_classes_path.to_string()),
            false => SemanticsMap::new(),
        };

        // semantics_map.dump_to_file();

        TermRewriter {
            rules_map: semantics_map.gen_rules_map(),
        }
    }

    fn get_rule(&self, expr: &LinearExpr) -> Option<&LinearizedExpr> {
        match self.rules_map.get(&expr) {
            Some(entry) => entry.choose(&mut thread_rng()),
            None => None,
        }
    }

    fn replace_all_occurrences(
        expr: &mut LinearizedExpr,
        replacement: LinearizedExpr,
        var_name: &str,
    ) {
        expr.replace_subexpr(&reg(var_name, replacement.size()), &replacement);
    }

    fn rand_sub_expr(expr: &LinearizedExpr, acceptance: f64) -> (usize, usize, LinearizedExpr) {
        let choose_top: bool = thread_rng().gen::<f64>() <= acceptance;
        let sizes = expr.get_sizes();

        let (mut index, mut size) = match choose_top {
            true => {
                let mut combined: Vec<(usize, usize)> =
                    sizes.iter().enumerate().map(|(i, s)| (i, *s)).collect();
                /* sort by size from high to low */
                combined.sort_by(|x, y| y.1.partial_cmp(&x.1).unwrap());
                /* choose only from 10 largest sub-nodes in AST*/
                let i = thread_rng().gen::<usize>() % (10.min(combined.len()));

                /* */
                (combined[i].0, combined[i].1)
            }
            false => {
                let i = thread_rng().gen::<usize>() % sizes.len();
                (i, sizes[i])
            }
        };

        while size == 1 && sizes.len() > 1 {
            index = thread_rng().gen::<usize>() % sizes.len();
            size = sizes[index];
        }

        let start = 1 + index - size;
        let end = index + 1;
        let sub_expr = expr.get_expression_slice(start, end);

        (start, end, sub_expr)
    }

    fn replace_expression(
        expr: &LinearizedExpr,
        sub_expr: &LinearizedExpr,
        start: usize,
        end: usize,
    ) -> LinearizedExpr {
        LinearizedExpr::new(
            expr.0[0..start]
                .iter()
                .chain(sub_expr.0.iter())
                .chain(&expr.0[end..])
                .cloned()
                .collect(),
        )
    }

    fn rand_var(size: usize) -> LinearizedExpr {
        let coin = thread_rng().gen::<usize>() % 4;
        match coin {
            0 => semantic_downcast(reg("x", 64), size),
            1 => semantic_downcast(reg("y", 64), size),
            2 => semantic_downcast(reg("c", 64), size),
            3 => semantic_downcast(reg("k", 64), size),
            _ => unreachable!(),
        }
    }

    fn pad_with_var(rule: &mut LinearizedExpr) {
        TermRewriter::replace_all_occurrences(rule, TermRewriter::rand_var(rule.size()), "p1");
        TermRewriter::replace_all_occurrences(rule, TermRewriter::rand_var(rule.size()), "p2");
    }

    fn replace_expr_with_rule(expr: &LinearizedExpr, rule: &LinearizedExpr) -> LinearizedExpr {
        let mut rule = rule.clone();

        let sizes = expr.get_sizes();
        let mut end = sizes.len() - 1;
        let mut start = end;

        /* replace variable or constant */
        if expr.op().arity() == 0 {
            let foo = match expr.op().op {
                LinearExprOp::Reg(ref s) => reg(s, expr.size()),
                LinearExprOp::Const(x) => constant(x, expr.size()),
                _ => unreachable!(),
            };
            TermRewriter::replace_all_occurrences(&mut rule, foo, "p0");
        }

        for index in (0..expr.op().arity()).into_iter().rev() {
            let var_name = format!("p{}", index);

            end = start;
            start = end - sizes[end - 1];
            let expr_slice = expr.get_expression_slice(start, end);

            TermRewriter::replace_all_occurrences(&mut rule, expr_slice, &var_name);
        }

        TermRewriter::pad_with_var(&mut rule);

        rule
    }

    pub fn rewrite_expr(&self, mut expr: LinearizedExpr) -> LinearizedExpr {
        // n: number of recursive MBA applications - at least 20, max 30
        let n = 20 + (thread_rng().gen::<usize>() % 11);
        for index in 0..n {
            let acceptance: f64 = match index {
                0..=1 => 0.7,
                _ => 0.05,
            };
            let (start, end, mut sub_expr) = TermRewriter::rand_sub_expr(&expr, acceptance);

            if let Some(rule) = match sub_expr.is_var() || sub_expr.is_constant() {
                true => self.get_rule(&reg("p0", sub_expr.size()).op()),
                false => self.get_rule(&sub_expr.op()),
            } {
                sub_expr = TermRewriter::replace_expr_with_rule(&sub_expr, rule);
                expr = TermRewriter::replace_expression(&expr, &sub_expr, start, end);
            }
        }

        expr.simplify()
    }

    pub fn rewrite_top_level_expr(&self, mut expr: LinearizedExpr) -> LinearizedExpr {
        if let Some(rule) = self.get_rule(&expr.op()) {
            expr = TermRewriter::replace_expr_with_rule(&expr, rule);
        }

        expr.simplify()
    }
}
