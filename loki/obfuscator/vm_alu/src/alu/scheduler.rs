use crate::alu::semantics_builder::SemanticsBlock;
use crate::config::CONFIG;
use intermediate_language::il::linearized_expressions::{LinearExprOp, LinearizedExpr};
use itertools::Itertools;
use std::collections::{HashMap, HashSet};

use serde::{Deserialize, Serialize};

use rand::prelude::*;
use rand::seq::SliceRandom;
use rand::thread_rng;

#[derive(Clone, Hash, Eq, PartialEq, Debug, Serialize, Deserialize)]
pub struct SchedulerIndex {
    pub alu_index: usize,
    pub key_index: usize,
}

impl SchedulerIndex {
    pub fn new(alu_index: usize, key_index: usize) -> SchedulerIndex {
        SchedulerIndex {
            alu_index,
            key_index,
        }
    }
}
#[derive(Debug, Serialize, Deserialize)]
pub struct SchedulerMap {
    pub map: HashMap<usize, SchedulerIndex>,
}

impl SchedulerMap {
    pub fn new() -> SchedulerMap {
        SchedulerMap {
            map: HashMap::new(),
        }
    }
}
#[derive(Debug, Serialize, Deserialize)]
pub struct ALUSemanticsMapEntry {
    pub key_index: usize,
    pub expr: LinearizedExpr,
}

impl ALUSemanticsMapEntry {
    pub fn new(key_index: usize, expr: LinearizedExpr) -> ALUSemanticsMapEntry {
        ALUSemanticsMapEntry { key_index, expr }
    }
}
#[derive(Debug, Serialize, Deserialize)]
pub struct ALUSemanticsMap {
    pub map: HashMap<usize, Vec<ALUSemanticsMapEntry>>,
}

impl ALUSemanticsMap {
    pub fn new() -> ALUSemanticsMap {
        ALUSemanticsMap {
            map: HashMap::new(),
        }
    }
}

pub struct SemanticsToSchedulerIndexMap {
    pub map: HashMap<LinearizedExpr, Vec<SchedulerIndex>>,
}

impl SemanticsToSchedulerIndexMap {
    pub fn new() -> SemanticsToSchedulerIndexMap {
        SemanticsToSchedulerIndexMap {
            map: HashMap::new(),
        }
    }
}

pub struct Scheduler {}

impl Scheduler {
    pub fn schedule_keys(blocks: &Vec<SemanticsBlock>) -> (SchedulerMap, ALUSemanticsMap) {
        match CONFIG.schedule_non_deterministic {
            true => Scheduler::schedule_keys_non_deterministic(blocks),
            false => Scheduler::schedule_keys_deterministic(blocks),
        }
    }

    pub fn schedule_keys_deterministic(
        blocks: &Vec<SemanticsBlock>,
    ) -> (SchedulerMap, ALUSemanticsMap) {
        /* start by 1 */
        let alu_indices: Vec<_> = (CONFIG.num_reserved_alu_handler..=CONFIG.num_alus)
            .into_iter()
            .collect();
        let key_indices: Vec<_> = (0..CONFIG.max_semantics_per_alu).into_iter().collect();
        let mut scheduler_indices = alu_indices
            .into_iter()
            .cartesian_product(key_indices.into_iter())
            .map(|(alu_index, key_index)| SchedulerIndex::new(alu_index, key_index));
        let mut scheduler_map = SchedulerMap::new();
        let mut alu_map = ALUSemanticsMap::new();
        for (block_index, block) in blocks.iter().enumerate() {
            let scheduler_index = match &block.expr.is_memory_op() {
                true => Scheduler::get_memory_keys(&block.expr),
                false => scheduler_indices
                    .next()
                    .expect("No scheduler index remaining."),
            };

            /* map alu to key and expression */
            Scheduler::map_alu_to_key_and_expr(&mut alu_map, block, &scheduler_index);

            /* map semantics block to alu and key */
            scheduler_map.map.insert(block_index, scheduler_index);
        }

        (scheduler_map, alu_map)
    }

    fn get_memory_keys(expr: &LinearizedExpr) -> SchedulerIndex {
        match expr.op().op {
            /* handler 1, key index 0*/
            LinearExprOp::Load => SchedulerIndex::new(1, 0),
            /* handler 1, key index 1*/
            LinearExprOp::Store => SchedulerIndex::new(1, 1),
            /* handler 1, key index 2*/
            LinearExprOp::Alloc(_) => SchedulerIndex::new(1, 2),
            _ => unreachable!(),
        }
    }

    pub fn schedule_keys_non_deterministic(
        blocks: &Vec<SemanticsBlock>,
    ) -> (SchedulerMap, ALUSemanticsMap) {
        let mut scheduler_map = SchedulerMap::new();
        let mut semantics_to_scheduler_index_map = SemanticsToSchedulerIndexMap::new();
        let mut alu_map = ALUSemanticsMap::new();
        let mut used_indices = HashSet::new();

        for (block_index, block) in blocks.iter().enumerate() {
            /* map semantics block to alu and key */
            let scheduler_index = Scheduler::get_scheduler_index(
                block,
                &mut alu_map,
                &mut semantics_to_scheduler_index_map,
                &mut used_indices,
            );
            scheduler_map.map.insert(block_index, scheduler_index);
        }

        (scheduler_map, alu_map)
    }

    fn reuse_scheduler_index() -> bool {
        /* return true with probability 2/3 */
        !CONFIG.handler_duplication || thread_rng().gen::<u64>() % 3 != 0
    }

    fn get_scheduler_index(
        block: &SemanticsBlock,
        alu_map: &mut ALUSemanticsMap,
        semantics_to_scheduler_index_map: &mut SemanticsToSchedulerIndexMap,
        used_indices: &mut HashSet<SchedulerIndex>,
    ) -> SchedulerIndex {
        match semantics_to_scheduler_index_map.map.get(&block.expr) {
            Some(scheduler_indices) if Scheduler::reuse_scheduler_index() => scheduler_indices
                .choose(&mut thread_rng())
                .expect("scheduler_indices is empty")
                .clone(),
            _ => Scheduler::get_new_scheduler_index(
                block,
                alu_map,
                semantics_to_scheduler_index_map,
                used_indices,
            ),
        }
    }

    fn get_new_scheduler_index(
        block: &SemanticsBlock,
        alu_map: &mut ALUSemanticsMap,
        semantics_to_scheduler_index_map: &mut SemanticsToSchedulerIndexMap,
        used_indices: &mut HashSet<SchedulerIndex>,
    ) -> SchedulerIndex {
        let scheduler_index = match block.expr.is_memory_op() {
            true => Scheduler::get_memory_keys(&block.expr),
            false => Scheduler::get_fresh_scheduler_index(used_indices),
        };

        Scheduler::map_alu_to_key_and_expr(alu_map, block, &scheduler_index);

        Scheduler::map_semantics_to_scheduler_index(
            semantics_to_scheduler_index_map,
            block,
            &scheduler_index,
        );

        scheduler_index
    }

    fn map_alu_to_key_and_expr(
        alu_map: &mut ALUSemanticsMap,
        block: &SemanticsBlock,
        scheduler_index: &SchedulerIndex,
    ) {
        let alu_map_entry =
            ALUSemanticsMapEntry::new(scheduler_index.key_index, block.expr.clone());
        alu_map
            .map
            .entry(scheduler_index.alu_index)
            .or_insert(vec![])
            .push(alu_map_entry);
    }
    fn map_semantics_to_scheduler_index(
        semantics_to_scheduler_index_map: &mut SemanticsToSchedulerIndexMap,
        block: &SemanticsBlock,
        scheduler_index: &SchedulerIndex,
    ) {
        semantics_to_scheduler_index_map
            .map
            .entry(block.expr.clone())
            .or_insert(vec![])
            .push(scheduler_index.clone());
    }

    fn get_fresh_scheduler_index(used_indices: &mut HashSet<SchedulerIndex>) -> SchedulerIndex {
        /* TODO: potential infinite loop for too small alu and semantics_per_alu bounds*/
        assert!(
            used_indices.len() < CONFIG.num_alus * CONFIG.max_semantics_per_alu,
            "Not enough space for handler semantics."
        );
        loop {
            /* alu_index starts at 1*/
            let alu_index = (thread_rng().gen::<usize>()
                % (CONFIG.num_alus - CONFIG.num_reserved_alu_handler))
                + CONFIG.num_reserved_alu_handler;
            assert!(
                0 < alu_index && alu_index <= CONFIG.num_alus,
                "ALU index is {}", alu_index
            );
            let key_index = thread_rng().gen::<usize>() % CONFIG.max_semantics_per_alu;
            assert!(
                key_index <= CONFIG.max_semantics_per_alu,
                "key index is {}", key_index
            );

            let scheduler_index = SchedulerIndex::new(alu_index, key_index);
            if !used_indices.contains(&scheduler_index) {
                used_indices.insert(scheduler_index.clone());

                return scheduler_index;
            }
        }
    }
}
