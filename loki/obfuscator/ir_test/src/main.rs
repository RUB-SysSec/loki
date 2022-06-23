extern crate intermediate_language;
extern crate ir_test;
extern crate rand;
extern crate seer_z3;

use intermediate_language::il::assignment::Assignment;
use intermediate_language::il::expression_utils::{constant, reg};
use intermediate_language::il::linearized_expressions::{LinearExpr, LinearExprOp, LinearizedExpr};
use intermediate_language::il::semantic_formula::SemanticFormula;
use intermediate_language::il::ssa::SSA;
use intermediate_language::il::z3::TranslatorZ3;
use intermediate_language::symbolic_execution::semantic_formula_evaluator::SemanticFormulaEvaluator;
use ir_test::grammar::{gen_expr_with_depth, gen_var};
use rand::thread_rng;
use rand::Rng;
use seer_z3 as z3;

fn gen_output(size: usize) -> LinearizedExpr {
    reg("o", size)
}

fn gen_formula(assignment: &Assignment) -> SemanticFormula {
    SemanticFormula::new(vec![assignment.clone()])
}

fn gen_symbols(num_vars: usize, size: usize) -> Vec<LinearExpr> {
    let mut ret = vec![LinearExpr::new(LinearExprOp::Reg("o".to_string()), size)];
    ret.push(LinearExpr::new(LinearExprOp::Reg("o1".to_string()), size));

    for i in 0..num_vars {
        let name = format!("R{}", i);
        ret.push(LinearExpr::new(LinearExprOp::Reg(name), size));
    }

    ret
}

fn rand_const(size: usize) -> LinearizedExpr {
    constant(gen_val_of_rand_size(), size)
}

fn gen_val_of_rand_size() -> u64 {
    let coin = thread_rng().gen::<usize>() % 5;
    match coin {
        0 => thread_rng().gen::<u8>() as u64,
        1 => thread_rng().gen::<u16>() as u64,
        2 => thread_rng().gen::<u32>() as u64,
        3 => thread_rng().gen::<u64>(),
        4 => gen_special_values(),
        _ => unreachable!(),
    }
}

fn gen_special_values() -> u64 {
    let coin = thread_rng().gen::<usize>() % 11;

    match coin {
        0 => 0x0,
        1 => 0x1,
        2 => 0x2,
        3 => 0x80,
        4 => 0xff,
        5 => 0x8000,
        6 => 0xffff,
        7 => 0x8000_0000,
        8 => 0xffff_ffff,
        9 => 0x8000_0000_0000_0000,
        10 => 0xffff_ffff_ffff_ffff,
        _ => unreachable!(),
    }
}

fn gen_constraints(num_vars: usize, size: usize) -> Vec<Assignment> {
    (0..num_vars)
        .into_iter()
        .map(|index| Assignment::new(gen_var(index, size), rand_const(size)))
        .collect()
}

fn rand_size() -> usize {
    let coin = thread_rng().gen::<usize>() % 4;
    match coin {
        0 => 8,
        1 => 16,
        2 => 32,
        3 => 64,
        _ => unreachable!(),
    }
}

fn eval_se_io(expr: &LinearizedExpr, constraints: &[Assignment], num_vars: usize) -> u64 {
    let mut se_engine = SemanticFormulaEvaluator::new(gen_symbols(num_vars, expr.size()));

    for c in constraints {
        se_engine.eval_instruction_formular(&gen_formula(c));
    }

    let output = gen_output(expr.size());
    let assignment = Assignment::new(output.clone(), expr.clone());
    let formula = gen_formula(&assignment);

    se_engine.eval_instruction_formular(&formula);

    se_engine.symbolic_state.get_var(&output).get_constant_val()
}

fn eval_z3_io(expr: &LinearizedExpr, constraints: &[Assignment]) -> u64 {
    // maximum size for model values
    assert!(expr.size() <= 64);
    let config = z3::Config::new();
    let context = z3::Context::new(&config);
    let solver = z3::Solver::new(&context);

    let translator = TranslatorZ3::new(&context);
    let expr_z3 = translator.translate(expr);

    for c in constraints {
        let lhs_z3 = translator.translate(&c.lhs);
        let rhs_z3 = translator.translate(&c.rhs);
        let ass = lhs_z3._eq(&rhs_z3);
        solver.assert(&ass);
    }

    let output = context.named_bitvector_const("o", expr.size() as u32);
    let assignment = output._eq(&expr_z3);

    solver.assert(&assignment);

    let sat = solver.check();
    assert!(sat);
    let model = solver.get_model();
    let output_val = model.eval(&output).unwrap().as_u64().unwrap();

    output_val
}

fn eval_se(expr: &LinearizedExpr, num_vars: usize) -> LinearizedExpr {
    let mut se_engine = SemanticFormulaEvaluator::new(gen_symbols(num_vars, expr.size()));
    let output = gen_output(expr.size());
    let assignment = Assignment::new(output.clone(), expr.clone());
    let formula = gen_formula(&assignment);
    se_engine.eval_instruction_formular(&formula);

    se_engine.symbolic_state.get_var(&output)
}

fn prove_semantic_equivalence(
    expr: &LinearizedExpr,
    simple_expr: &LinearizedExpr,
    var_size: usize,
    depth: usize,
) {
    let config = z3::Config::new();
    let context = z3::Context::new(&config);
    let solver = z3::Solver::new(&context);
    let translator = TranslatorZ3::new(&context);

    let expr_z3 = translator.translate(expr);
    let simple_expr_z3 = translator.translate(simple_expr);

    let assignment = z3::Ast::not(&expr_z3._eq(&simple_expr_z3));
    solver.assert(&assignment);

    let sat = solver.check();
    if sat {
        println!("var size: {}", var_size);
        println!("expr size: {}", expr.size());
        println!("expr depth: {}", depth + 1);
        println!("expr: {}", expr.to_infix());
        println!("simple_expr: {}", simple_expr.to_infix());

        let model = solver.get_model();
        let r0_value = context.named_bitvector_const("R0", var_size as u32);
        let r0_val = model.eval(&r0_value).unwrap().as_u64().unwrap();
        let r1_value = context.named_bitvector_const("R1", var_size as u32);
        let r1_val = model.eval(&r1_value).unwrap().as_u64().unwrap();
        println!("model: R0={}, R1={}", r0_val, r1_val);

        println!("\n\n");
    }
}

fn eval_ssa(expr: &LinearizedExpr, num_vars: usize) -> LinearizedExpr {
    let output = gen_output(expr.size());
    let ssa = SSA::from_assignments(&vec![Assignment::new(output, expr.clone())]);

    let mut se_engine = SemanticFormulaEvaluator::new(gen_symbols(num_vars, expr.size()));

    for assignment in &ssa {
        let formula = gen_formula(&assignment);
        se_engine.eval_instruction_formular(&formula);
    }

    let last_var_lhs = &ssa.last().unwrap().lhs;

    se_engine.symbolic_state.get_var(&last_var_lhs)
}

fn test_io_behavior(max_depth: usize, num_vars: usize, n: usize) {
    println!("Testing I/O behavior");
    for _ in 0..n {
        let size = rand_size();
        let depth = thread_rng().gen::<usize>() % max_depth + 1;
        let expr = gen_expr_with_depth(num_vars, depth, size);

        let constraints = gen_constraints(num_vars, size);

        if expr.size() > 64 {
            continue;
        }

        let r_se = eval_se_io(&expr, &constraints, num_vars);
        let r_z3 = eval_z3_io(&expr, &constraints);

        if r_se != r_z3 {
            for c in constraints {
                println!("constraint: {}", c.to_string());
            }
            println!("var size: {}", size);
            println!("expr size: {}", expr.size());
            println!("expr depth: {}", depth + 1);
            println!("expr: {}", expr.to_infix());
            println!("result: z3 -- 0x{:x} -- se -- 0x{:x}", r_z3, r_se);
            println!("\n\n")
        }
    }
}

fn test_simplifications(max_depth: usize, num_vars: usize, n: usize) {
    println!("Testing semantic equivalence");
    for _ in 0..n {
        let size = rand_size();
        let depth = thread_rng().gen::<usize>() % max_depth;
        let expr = gen_expr_with_depth(num_vars, depth, size);

        if expr.size() > 64 {
            continue;
        }

        let simple_expr = eval_se(&expr, num_vars);
        prove_semantic_equivalence(&expr, &simple_expr, size, depth);
    }
}

fn test_ssa(max_depth: usize, num_vars: usize, n: usize) {
    println!("Testing SSA");
    for _ in 0..n {
        let size = rand_size();
        let depth = thread_rng().gen::<usize>() % max_depth;
        let expr = gen_expr_with_depth(num_vars, depth, size);

        if expr.size() > 64 {
            continue;
        }

        let ssa_expr = eval_ssa(&expr, num_vars);
        let simplified_expr = eval_se(&expr, num_vars);

        if ssa_expr != simplified_expr {
            println!("var size: {}", size);
            println!("expr size: {}", expr.size());
            println!("expr depth: {}", depth + 1);
            println!("expr: {}", expr.to_infix());
            println!("ssa: {}", ssa_expr.to_infix());
            println!("se: {}", simplified_expr.to_infix());
            println!("\n\n")
        }
    }
}

fn main() {
    let max_depth = 5;
    let num_vars = 3;

    test_io_behavior(max_depth, num_vars, 4000);
    test_simplifications(max_depth, num_vars, 4000);
    test_ssa(max_depth, num_vars, 4000);
}
