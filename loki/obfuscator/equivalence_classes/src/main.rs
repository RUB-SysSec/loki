use equivalence_classes::semantics_map::SemanticsMap;
use equivalence_classes::synthesizer::EquivClassSynthesizer;
use intermediate_language::il::expression_utils::*;
use intermediate_language::il::linearized_expressions::LinearizedExpr;
use intermediate_language::{FastHashMap, FastHashSet};
use std::env;
use std::process::exit;

fn gen_basic_semantics(size: usize) -> Vec<LinearizedExpr> {
    vec![
        reg("p0", size),
        add(reg("p0", size), reg("p1", size), size),
        sub(reg("p0", size), reg("p1", size), size),
        or(reg("p0", size), reg("p1", size), size),
        xor(reg("p0", size), reg("p1", size), size),
        and(reg("p0", size), reg("p1", size), size),
        nand(reg("p0", size), reg("p1", size), size),
        nor(reg("p0", size), reg("p1", size), size),
        not(reg("p0", size), size),
        neg(reg("p0", size), size),
        shl(reg("p0", size), reg("p1", size), size),
        mul(reg("p0", size), reg("p1", size), size),
    ]
}

fn print_equiv_classes(equivalence_classes: &FastHashMap<String, FastHashSet<LinearizedExpr>>) {
    let filtered = equivalence_classes.values().filter(|c| c.len() >= 1);
    for c in filtered {
        print_equiv_class(&sort_equiv_class(c));
    }
}

fn sort_equiv_class(equiv_class: &FastHashSet<LinearizedExpr>) -> Vec<LinearizedExpr> {
    let mut v: Vec<_> = equiv_class.iter().map(|x| x.clone()).collect();
    v.sort_by(|a, b| a.depth().cmp(&b.depth()));
    v
}

fn print_equiv_class(equiv_class: &Vec<LinearizedExpr>) {
    println!("representative: {}", equiv_class[0].to_string());

    for member in &equiv_class.as_slice()[1..equiv_class.len()] {
        println!("{}", member.to_string());
    }
    println!("\n\n\n");
}

fn main() {
    let args = env::args().collect::<Vec<_>>();
    match args.len() {
        4 => {}
        _ => {
            println!(
                "[x] Syntax> {} <expr depth> <bit size> <output file>",
                args[0]
            );
            exit(0)
        }
    }

    let expr_depth = args
        .get(1)
        .expect("No expression depth provided.")
        .parse()
        .expect("Could not parse as expr_depth");
    let size = args
        .get(2)
        .expect("No expression size provided.")
        .parse()
        .expect("Could not parse size.");
    let output_file = args.get(3).expect("No output file provided.");

    let num_io_samples = 1000;
    let equiv_classes_file = "./equiv_classes.json".to_string();

    let basic_semantics = gen_basic_semantics(size);

    let mut synthesizer = EquivClassSynthesizer::new(num_io_samples, size);
    synthesizer.init_with_selection(&basic_semantics);
    synthesizer.verbose = true;
    synthesizer.synthesize(expr_depth);

    let mut semantics_map = SemanticsMap::new();

    for expr in basic_semantics {
        let equiv_class = synthesizer.determine_equiv_class(&expr);
        semantics_map.insert(
            expr,
            synthesizer
                .equiv_classes
                .get(&equiv_class)
                .unwrap()
                .iter()
                .cloned()
                .collect::<Vec<_>>(),
        );
    }

    semantics_map.serialize_to_file(&output_file);
    semantics_map.dump_to_file();

    synthesizer.serialize_to_file(&equiv_classes_file);
    print_equiv_classes(&synthesizer.equiv_classes);
}
