use crate::alu::scheduler::SchedulerMap;
use crate::bytecode::keys::MetaALUKeys;
use crate::llvm::llvm_input_data::LLVMInputData;
use intermediate_language::il::assignment::Assignment;
use std::collections::HashMap;
use std::fs::File;
use std::io::Write;

pub struct ByteCodeTranslator {
    pub variable_map: HashMap<String, usize>,
}

impl ByteCodeTranslator {
    pub fn new() -> ByteCodeTranslator {
        ByteCodeTranslator {
            variable_map: HashMap::new(),
        }
    }

    fn dump_bytecode(&self, workdir: &String, bytecode: Vec<u8>) {
        let mut file = File::create(format!("{}/byte_code.bin", workdir)).unwrap();
        file.write_all(&bytecode).unwrap();
    }

    fn dump_variable_map(&mut self, workdir: &String, llvm_input_data: &LLVMInputData) {
        let mut map_str = String::new();

        for var_name in &llvm_input_data.arguments {
            map_str.push_str(&format!(
                "{} {:#x}\n",
                var_name,
                self.get_mut_var_index(var_name)
            ));
        }

        let mut file = File::create(format!("{}/variable_map.txt", workdir)).unwrap();
        write!(&mut file, "{}", map_str).unwrap();
    }

    fn get_mut_var_index(&mut self, name: &String) -> usize {
        // out_reg at 0
        match name.as_str() {
            "out_reg" => return 0,
            _ => {}
        }

        if let Some(entry) = self.variable_map.get(name) {
            return *entry;
        }
        // skip out_reg at 0 and vIP at 1
        let index = self.variable_map.len() + 2;
        self.variable_map.insert(name.to_string(), index);

        index
    }

    fn translate_to_bytecode(
        &mut self,
        llvm_input_data: &LLVMInputData,
        keys: &MetaALUKeys,
        scheduler_map: &SchedulerMap,
    ) -> Vec<u8> {
        let mut ret = vec![];

        for (block_index, block) in llvm_input_data.blocks.iter().enumerate() {
            let scheduler_map_entry = &scheduler_map.map[&block_index];
            let mut rhs: Vec<u8> = vec![];

            // add opcode => OP
            rhs.extend_from_slice(&(scheduler_map_entry.alu_index as u16).to_le_bytes());
            assert_eq!(rhs.len(), 2);

            // add R0 => OP R0
            rhs.extend_from_slice(
                &(self.get_mut_var_index(&block.output_variable.get_var_name().to_string()) as u16)
                    .to_le_bytes(),
            );
            assert_eq!(rhs.len(), 4);

            // add R1 and R2 => OP R0 R1 R2
            match block.input_variables.len() {
                0 => rhs.extend(
                    /* set reg_1 to vIP such that dummy operations do not break */
                    (1 as u16)
                        .to_le_bytes()
                        .iter()
                        /* set reg_2 to vIP such that dummy operations do not break */
                        .chain((1 as u16).to_le_bytes().iter()),
                ),
                1 => rhs.extend(
                    (self.get_mut_var_index(&block.input_variables[0].get_var_name().to_string())
                        as u16)
                        .to_le_bytes()
                        .iter()
                        /* set reg_2 to vIP such that dummy operations do not break */
                        .chain((1 as u16).to_le_bytes().iter()),
                ),
                2 => rhs.extend(
                    (self.get_mut_var_index(&block.input_variables[0].get_var_name().to_string())
                        as u16)
                        .to_le_bytes()
                        .iter()
                        .chain(
                            (self.get_mut_var_index(
                                &block.input_variables[1].get_var_name().to_string(),
                            ) as u16)
                                .to_le_bytes()
                                .iter(),
                        ),
                ),
                _ => unreachable!(),
            }
            assert_eq!(rhs.len(), 8);

            // add immediate => OP R0 R1 R2 IMM
            match block.immediate {
                Some(imm) => rhs.extend_from_slice(&(imm as u64).to_le_bytes()),
                _ => rhs.extend_from_slice(&(0 as u64).to_le_bytes()),
            }
            assert_eq!(rhs.len(), 16);

            // add key => OP R0 R1 R2 IMM K
            let key = keys
                .get(&scheduler_map_entry.alu_index)
                .expect(&format!(
                    "Could not access ALU index {}",
                    &scheduler_map_entry.alu_index
                ))
                .get(scheduler_map_entry.key_index);
            rhs.extend_from_slice(&(key as u64).to_le_bytes());

            // add to return data
            ret.extend(&rhs);

            assert_eq!(rhs.len(), 24);
        }

        ret
    }

    pub fn process_data(
        workdir: &String,
        llvm_input_data: &LLVMInputData,
        keys: MetaALUKeys,
        scheduler_map: SchedulerMap,
    ) -> (Vec<u8>, Vec<u16>) {
        let mut translator = ByteCodeTranslator::new();

        let bytecode = translator.translate_to_bytecode(llvm_input_data, &keys, &scheduler_map);

        translator.dump_variable_map(workdir, llvm_input_data);
        // dump_variable_map may modify the variable map to add unused inputs, thus it must be executed before to_debug_file
        translator.to_debug_file(&workdir, &llvm_input_data.instructions, &bytecode);
        translator.dump_bytecode(&workdir, bytecode.clone());

        (
            bytecode,
            llvm_input_data
                .arguments
                .iter()
                .map(|a| translator.variable_map[a] as u16)
                .collect(),
        )
    }

    pub fn to_string(&self, assignments: &Vec<Assignment>, bytecode: &Vec<u8>) -> String {
        let mut ret = String::new();
        for (index, b) in bytecode.chunks(24).enumerate() {
            ret.push_str(&format!("{}\n", assignments[index].to_string()));
            ret.push_str(&format!("{:02x}{:02x}", b[0], b[1]));
            ret.push_str(" ");
            ret.push_str(&format!("{:02x}{:02x}", b[2], b[3]));
            ret.push_str(" ");
            ret.push_str(&format!("{:02x}{:02x}", b[4], b[5]));
            ret.push_str(" ");
            ret.push_str(&format!("{:02x}{:02x}", b[6], b[7]));
            ret.push_str(" ");
            ret.push_str(&format!(
                "{:02x}{:02x}{:02x}{:02x}{:02x}{:02x}{:02x}{:02x}",
                b[8], b[9], b[10], b[11], b[12], b[13], b[14], b[15]
            ));
            ret.push_str(" ");
            ret.push_str(&format!(
                "{:02x}{:02x}{:02x}{:02x}{:02x}{:02x}{:02x}{:02x}\n",
                b[16], b[17], b[18], b[19], b[20], b[21], b[22], b[23]
            ));
        }

        ret.push_str("\n\n");
        ret.push_str("variable map:\n");
        for (k, v) in self.variable_map.iter() {
            ret.push_str(&format!("{}: {:04x}\n", k, v));
        }

        ret
    }

    pub fn to_debug_file(
        &self,
        workdir: &String,
        assignments: &Vec<Assignment>,
        bytecode: &Vec<u8>,
    ) {
        let content = self.to_string(assignments, bytecode);
        let mut file = File::create(format!("{}/debug_files/byte_code.txt", workdir)).unwrap();
        write!(&mut file, "{}", content).unwrap();
    }
}
