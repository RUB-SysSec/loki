use intermediate_language::il::expression_utils::*;
use vm_alu::alu::postprocessor::ALUPostProcessor;
use vm_alu::alu::semantics_builder::SemanticsBuilder;
use vm_alu::bytecode::keys::ALUKeys;
use vm_alu::smt::thwart::{
    constraint_key_with_primes, constraint_with_key, synthesize_point_function, thwart,
};
use vm_alu::synthesis::mba::{rewrite_to_equivalent_mba, rewrite_to_equivalent_mba_top_level};
use vm_alu::term_rewriting::term_rewriter::TermRewriter;

use intermediate_language::il::z3::TranslatorZ3PythonString;
use rand::prelude::*;
use rand::thread_rng;
use std::process::exit;
use std::env;

#[allow(dead_code)]
enum KeyType {
    Factorization,
    PointFunction,
    All,
}

pub fn main() {
    let args: Vec<String> = env::args().collect();
    if args.len() < 2 {
        eprintln!("Missing argument: {} factorization|pointfunction|all", &args[0]);
        exit(1);
    }
    let key_type = match &(&args[1].to_lowercase()).as_str() {
        &"factorization" => KeyType::Factorization,
        &"pointfunction" => KeyType::PointFunction,
        &"all" => KeyType::All,
        _ => {unreachable!("Unknown key type: {}", &args[1])},
    };

    loop {
        /* same number of keys as is VM handler */
        let num_semantics = thread_rng().gen::<usize>() % 3 + 3;
        let term_rewriter = TermRewriter::new();
        let mut alu_keys = ALUKeys::new();
        let mut instructions = SemanticsBuilder::gen_semantics(num_semantics);

        /* our expression to check*/
        let core_expr = add64(reg("x", 64), reg("y", 64));
        instructions.push(core_expr.clone());

        /* init keys*/
        thwart(instructions.as_slice(), &mut alu_keys, &term_rewriter);

        /* grep first key_type key*/
        let index: Option<usize> = match key_type {
            KeyType::Factorization => (0..alu_keys.len())
                .into_iter()
                .filter(|i| alu_keys.contains_additional_key(*i))
                .nth(0),
            KeyType::PointFunction => (0..alu_keys.len())
                .into_iter()
                .filter(|i| !alu_keys.contains_additional_key(*i))
                .nth(0),
            KeyType::All => (0..alu_keys.len()).into_iter().nth(0),
        };

        /* if no key found -> restart */
        if index.is_none() {
            continue;
        }

        /* unwrap index */
        let index = index.unwrap();

        /* get constrainted expression in dependence on key_type */
        let expr = match key_type {
            KeyType::Factorization => constraint_key_with_primes(&alu_keys, index, &term_rewriter),
            KeyType::PointFunction => {
                let synthesized = synthesize_point_function(&alu_keys, index);
                /* restart if nothing found */
                if !synthesized.is_some() {
                    continue;
                }
                rewrite_to_equivalent_mba(synthesized.unwrap(), &term_rewriter)
            }
            KeyType::All => constraint_with_key(&alu_keys, index, &term_rewriter),
        };

        /* apply mba-obfuscations as in thwart*/
        let f = ALUPostProcessor::rewrite_expression(rewrite_to_equivalent_mba_top_level(
            mul64(
                expr,
                rewrite_to_equivalent_mba(core_expr.clone(), &term_rewriter),
            ),
            &term_rewriter,
        ));

        println!("{}", TranslatorZ3PythonString::translate(&f));

        return;
    }
}
