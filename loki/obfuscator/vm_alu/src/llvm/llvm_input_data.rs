use crate::alu::semantics_builder::SemanticsBlock;
use crate::alu::superoptimizer::SuperOptimizer;
use crate::config::CONFIG;
use crate::emulator::preprocessor::InputEmulationPreprocessor;
use crate::llvm::postprocessor::LLVMInputDataPostProcessor;
use intermediate_language::il::assignment::Assignment;
use serde::{Deserialize, Serialize};
use std::fs;
use std::fs::File;
use std::io::Write;

#[derive(Serialize, Deserialize)]
pub struct LLVMInputDataDeserialized {
    pub arguments: Vec<String>,
    pub instructions: Vec<Assignment>,
}

impl LLVMInputDataDeserialized {
    pub fn deserialize(file_path: &str) -> LLVMInputData {
        let file_content = fs::read_to_string(file_path).expect("File not found!");
        let input_data: LLVMInputDataDeserialized = serde_json::from_str(&file_content).unwrap();

        LLVMInputData {
            arguments: input_data.arguments,
            instructions: input_data.instructions.clone(),
            instructions_emulator: input_data.instructions,
            blocks: vec![],
        }
    }
}

pub struct LLVMInputData {
    pub arguments: Vec<String>,
    pub instructions: Vec<Assignment>,
    pub instructions_emulator: Vec<Assignment>,
    pub blocks: Vec<SemanticsBlock>,
}

impl LLVMInputData {
    pub fn from_file(workdir: &String, file_path: &str) -> LLVMInputData {
        /* deserialize */
        let mut input_data = LLVMInputDataDeserialized::deserialize(file_path);

        input_data.to_debug_file(&format!("{}/debug_files/llvm_input_initial.txt", workdir));

        // postprocess instructions
        input_data.instructions_emulator =
            InputEmulationPreprocessor::rewrite_assignments(input_data.instructions_emulator);

        input_data.instructions = LLVMInputDataPostProcessor::rewrite_assignments(
            input_data.instructions,
            &input_data.arguments,
        );

        input_data.to_debug_file(&format!(
            "{}/debug_files/llvm_input_after_preprocessing.txt",
            workdir
        ));

        /* supertoptimization*/
        if CONFIG.superoptimization {
            input_data.instructions = SuperOptimizer::run(input_data.instructions);
            input_data.to_debug_file(&format!(
                "{}/debug_files/llvm_input_after_superoptimization.txt",
                workdir
            ));
        }

        /* TODO: add blocks to debug output */
        input_data.blocks = input_data
            .instructions
            .iter()
            .map(|a| SemanticsBlock::from_assignment(&a))
            .collect();

        input_data
    }

    fn to_string(&self) -> String {
        let mut ret = String::new();

        ret.push_str("Instructions:\n");
        for i in &self.instructions {
            ret.push_str(&format!("{}\n", i.to_string()));
        }

        ret.push_str("\n");

        ret.push_str("Arguments:\n");
        for arg in &self.arguments {
            ret.push_str(&format!("{}\n", arg));
        }

        ret
    }

    fn to_debug_file(&self, file_name: &str) {
        self.verify();

        if !CONFIG.debug_output {
            return;
        }

        let mut file = File::create(file_name).unwrap();
        write!(&mut file, "{}", self.to_string()).unwrap();
    }

    fn verify(&self) {
        assert!(!self.instructions.is_empty(), "No LLVM instructions found.");
        assert!(
            !self.arguments.is_empty(),
            "No LLVM provided input arguments found."
        );
        assert!(
            !self.arguments.iter().any(|s| s.is_empty()),
            "Empty LLVM input argument provided."
        );
    }
}
