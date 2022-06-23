use crate::alu::alu::ALU;
use crate::alu::scheduler::{Scheduler, SchedulerMap};
use crate::alu::semantics_builder::SemanticsBlock;
use crate::bytecode::keys::MetaALUKeys;
use crate::config::CONFIG;
use crate::term_rewriting::term_rewriter::TermRewriter;
use intermediate_language::il::linearized_expressions::LinearizedExpr;
use rayon::prelude::*;
use rmp_serde;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::fs::File;
use std::io::Write;

#[derive(Debug, Serialize, Deserialize)]
pub struct MetaALU {
    pub keys: MetaALUKeys,
    pub scheduler_map: SchedulerMap,
    pub alu_semantics: HashMap<usize, LinearizedExpr>,
}

impl MetaALU {
    pub fn new(
        workdir: &String,
        input_semantics: &Vec<SemanticsBlock>,
        term_rewriter: &TermRewriter,
    ) -> MetaALU {
        let (scheduler_map, alu_map) = Scheduler::schedule_keys(input_semantics);

        let mut keys = MetaALUKeys::new();

        // let term_rewriter = TermRewriter::new();

        let alus: Vec<_> = (1..=CONFIG.num_alus)
            .into_par_iter()
            .map(|alu_index| {
                let mut alu = ALU::new(alu_index, alu_map.map.get(&alu_index), &term_rewriter);

                while !alu.verify() && alu_index > 1 {
                    alu = ALU::new(alu_index, alu_map.map.get(&alu_index), &term_rewriter);
                }
                alu.to_llvm(workdir);
                alu
            })
            .collect();

        let mut alu_semantics = HashMap::new();
        for alu in &alus {
            keys.insert(alu.index, alu.keys.clone());
            alu_semantics.insert(alu.index, alu.assignment.rhs.clone());
        }

        let meta_alu = MetaALU {
            keys,
            scheduler_map,
            alu_semantics,
        };

        if CONFIG.debug_output {
            let file_name = format!("{}/debug_files/meta_alu.bin", workdir);
            let content =
                rmp_serde::to_vec(&meta_alu).expect("Could not serialize original assignment");
            let mut file = File::create(&file_name).unwrap();
            file.write_all(&content)
                .expect(&format!("Could not write to {}", file_name));
        }

        meta_alu
    }
}
