pub struct Config {
    pub rewrite_mba: bool,
    pub superoptimization: bool,
    pub schedule_non_deterministic: bool,
    pub handler_duplication: bool,
    pub num_alus: usize,
    pub min_semantics_per_alu: usize,
    pub max_semantics_per_alu: usize,
    pub min_superhandler_depth: usize,
    pub max_superhandler_depth: usize,
    pub num_reserved_alu_handler: usize,
    pub equivalence_classes_path: &'static str,
    pub verification_iterations: usize,
    pub debug_output: bool,
    pub eval_dir: &'static str,
    pub num_instances: usize,
}

pub const CONFIG: Config = Config {
    rewrite_mba: false,
    superoptimization: true,
    schedule_non_deterministic: true,
    handler_duplication: false,
    num_alus: 511,
    min_semantics_per_alu: 3,
    max_semantics_per_alu: 5,
    min_superhandler_depth: 3,
    max_superhandler_depth: 12,
    num_reserved_alu_handler: 2,
    equivalence_classes_path: "./mba/",
    verification_iterations: 100,
    debug_output: false,
    eval_dir: "/home/tblazytko/evaluation/des/",
    num_instances: 256,
};
