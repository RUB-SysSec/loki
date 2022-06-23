use intermediate_language::il::linearized_expressions::LinearizedExpr;
use intermediate_language::il::z3::TranslatorZ3;

use seer_z3 as z3;

use std::env;
use std::process::exit;

use equivalence_classes::semantics_map::SemanticsMap;

pub fn semantically_equivalent(expr1: &LinearizedExpr, expr2: &LinearizedExpr) -> bool {
    let mut config = z3::Config::new();
    config.set_timeout_msec(5000);
    let context = z3::Context::new(&config);
    let solver = z3::Solver::new(&context);
    let translator = TranslatorZ3::new(&context);

    let expr1_z3 = translator.translate(expr1);
    let expr2_z3 = translator.translate(expr2);

    let assignment = z3::Ast::not(&expr1_z3._eq(&expr2_z3));
    solver.assert(&assignment);

    solver.check_unsat()
}

fn main() {
    let args = env::args().collect::<Vec<_>>();
    match args.len() {
        3 => {}
        _ => {
            println!(
                "[x] Syntax> {} <path to input file directory> <output file>",
                args[0]
            );
            exit(0)
        }
    }
    let path = args.get(1).expect("No path to input files provided.");
    let output_file = args.get(2).expect("No output file provided.");

    let semantics_map = SemanticsMap::new_from_parameter(
        SemanticsMap::unify_from_files(&path)
            .0
            .into_iter()
            .map(|(represenative, equiv_class)| {
                let before = equiv_class.len();
                let equiv_class: Vec<_> = equiv_class
                    .into_iter()
                    .filter(|expr| semantically_equivalent(&represenative, &expr))
                    .collect();
                println!(
                    "before: {} -- after: {} ({})",
                    before,
                    equiv_class.len(),
                    represenative.to_string()
                );
                (represenative, equiv_class)
            })
            .collect(),
    );

    semantics_map.serialize_to_file(&output_file);
}
