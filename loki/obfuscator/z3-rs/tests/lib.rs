#[macro_use]
extern crate log;
extern crate env_logger;

extern crate seer_z3 as z3;
use z3::*;

#[test]
fn test_config() {
    let _ = env_logger::init();
    let mut c = Config::new();
    c.set_proof_generation(true);
}

#[test]
fn test_context() {
    let _ = env_logger::init();
    let mut cfg = Config::new();
    cfg.set_proof_generation(true);
    let _ = Context::new(&cfg);
}

#[test]
fn test_sorts_and_symbols() {
    let _ = env_logger::init();
    let cfg = Config::new();
    let ctx = Context::new(&cfg);
    let _ = ctx.named_int_const("x");
    let _ = ctx.named_int_const("y");
}

#[test]
fn test_solving() {
    let _ = env_logger::init();
    let cfg = Config::new();
    let ctx = Context::new(&cfg);
    let x = ctx.named_int_const("x");
    let y = ctx.named_int_const("y");

    let solver = Solver::new(&ctx);
    solver.assert(&x.gt(&y));
    assert!(solver.check());
}

#[test]
fn test_solving_for_model() {
    let _ = env_logger::init();
    let cfg = Config::new();
    let ctx = Context::new(&cfg);
    let x = ctx.named_int_const("x");
    let y = ctx.named_int_const("y");
    let zero = ctx.from_i64(0);
    let two = ctx.from_i64(2);
    let seven = ctx.from_i64(7);

    let solver = Solver::new(&ctx);
    solver.assert(&x.gt(&y));
    solver.assert(&y.gt(&zero));
    solver.assert(&y.rem(&seven)._eq(&two));
    solver.assert(&x.add(&[&two]).gt(&seven));
    assert!(solver.check());

    let model = solver.get_model();
    let xv = model.eval(&x).unwrap().as_i64().unwrap();
    let yv = model.eval(&y).unwrap().as_i64().unwrap();
    info!("x: {}", xv);
    info!("y: {}", yv);
    assert!(xv > yv);
    assert!(yv % 7 == 2);
    assert!(xv + 2 > 7);
}
