use rayon::prelude::*;
use std::fs::create_dir_all;
use std::time::Instant;
use vm_alu::alu::meta_alu::MetaALU;
use vm_alu::bytecode::translator::ByteCodeTranslator;
use vm_alu::config::CONFIG;
use vm_alu::emulator::emulator::Verificator;
use vm_alu::llvm::llvm_input_data::LLVMInputData;
use vm_alu::term_rewriting::term_rewriter::TermRewriter;

fn generate_workdir(index: usize) -> String {
    let workdir = format!("{}/instances/vm_alu{:03}", CONFIG.eval_dir, index);

    create_dir_all(format!("{}/debug_files", workdir))
        .expect("Could not create directory debug_files.");
    create_dir_all(format!("{}/alus", workdir)).expect("Could not create directory alus.");

    workdir
}

fn main() {
    create_dir_all(format!("{}/instances", CONFIG.eval_dir))
        .expect("Could not create directory instances.");

    let term_rewriter = TermRewriter::new();

    let num_cpu = 52;

    let iterator: Vec<_> = (0..CONFIG.num_instances).into_iter().collect();

    for chunk in iterator.chunks(num_cpu) {
        chunk.into_par_iter().for_each(|index| {
            let workdir = generate_workdir(*index);
            let build_time = Instant::now();

            let llvm_input_data = LLVMInputData::from_file(
                &workdir,
                &format!("{}/src/lifted_input.txt", CONFIG.eval_dir),
            );

            let meta_alu = MetaALU::new(&workdir, &llvm_input_data.blocks, &term_rewriter);

            let (bytecode, arguments) = ByteCodeTranslator::process_data(
                &workdir,
                &llvm_input_data,
                meta_alu.keys,
                meta_alu.scheduler_map,
            );

            let build_time_seconds = build_time.elapsed().as_secs_f64();
            let verification_time = Instant::now();

            if CONFIG.verification_iterations > 0 && !Verificator::verify_transformation(
                &meta_alu.alu_semantics,
                &bytecode,
                &arguments,
                &llvm_input_data,
                CONFIG.verification_iterations,
            ) {
                assert!(false, "Verification failed!");
            }
            let file_name = format!("{}/timings.txt", workdir);
            let content = format!(
                "Build time: {},\nVerification time: {},\n",
                build_time_seconds,
                verification_time.elapsed().as_secs_f64()
            );
            std::fs::write(file_name, content).expect("Unable to write timings file");
        })
    }
}
