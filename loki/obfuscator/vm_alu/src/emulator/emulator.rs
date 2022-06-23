use crate::llvm::llvm_input_data::LLVMInputData;
use intermediate_language::il::assignment::Assignment;
use intermediate_language::il::expression_utils::*;
use intermediate_language::il::linearized_expressions::{LinearExpr, LinearExprOp, LinearizedExpr};
use intermediate_language::symbolic_execution::semantic_formula_evaluator::SemanticFormulaEvaluator;
use intermediate_language::utils::bit_vecs::{concat_val, mask_to_size, slice_val};
use rand::prelude::*;
use rand::thread_rng;
use rayon::iter::IntoParallelIterator;
use rayon::iter::ParallelIterator;
use std::collections::HashMap;
use std::convert::TryInto;

pub struct VMEmulator {}

impl VMEmulator {
    pub fn emulate(
        alu_semantics: &HashMap<usize, LinearizedExpr>,
        bytecode: &[u8],
        arguments: &Vec<(u16, u64)>,
        memory_bytes: &HashMap<usize, Vec<u64>>,
    ) -> u64 {
        // init variable state
        let mut register_state: HashMap<u16, u64> = HashMap::new();
        let mut memory_state: HashMap<u64, u8> = HashMap::new();

        // init variables and memory with random values
        for (index, arg) in arguments.iter().enumerate() {
            register_state.insert(arg.0, arg.1);

            for offset in 0..memory_bytes[&index].len() {
                let address = arg.1 + (offset as u64);
                memory_state.insert(address, memory_bytes[&index][offset] as u8);
            }
        }

        // init alloc
        let mut alloc_base = 0x800;

        // walk over each instruction
        for instr_bytes in bytecode.chunks(24) {
            // decode
            let (alu_num, r0, r1, r2, constant, key) = VMEmulator::decode_instruction(instr_bytes);

            // println!("alu index: 0x{:04x}", alu_num);
            // println!("r0: 0x{:04x}", r0);
            // println!("r1: 0x{:04x}", r1);
            // println!("r2: 0x{:04x}", r2);
            // println!("c: 0x{:08x}", constant);
            // println!("key: 0x{:08x}", key);

            // get values or handle vip reg
            let (v1, v2) = match (r1, r2) {
                // op zero
                (1, 1) => (0, 0),
                // op1
                (_, 1) => (*register_state.get(&r1).unwrap(), 0),
                // op2
                (_, _) => (
                    *register_state.get(&r1).unwrap(),
                    *register_state.get(&r2).unwrap(),
                ),
            };

            // evaluate expression
            match alu_num {
                // vm exit
                0 => unreachable!(),
                // memory handler
                1 => {
                    match key {
                        // load
                        0 => {
                            let address = register_state.get(&r1).unwrap();
                            let mut value = memory_state[&address] as u64;

                            for index in 1..(constant / 8) {
                                value = concat_val(
                                    memory_state[&(address + index)] as u64,
                                    value,
                                    ((index * 8) as u64).try_into().unwrap(),
                                );
                            }
                            *register_state.entry(r0).or_insert(0) = value;
                        }
                        // store
                        1 => {
                            let address = register_state.get(&r1).unwrap();
                            let value = *register_state.get(&r2).unwrap();

                            for index in 0..(constant / 8) {
                                *memory_state.entry(*address + index).or_insert(0) =
                                    slice_val(value, (index as u8) * 8, (index as u8) * 8 + 7) as u8
                            }
                            *register_state.entry(r0).or_insert(0) =
                                *register_state.get(&r2).unwrap();
                        }
                        // alloc
                        2 => {
                            for index in 0..constant {
                                *memory_state.entry(alloc_base + index).or_insert(0) = 0;
                            }

                            *register_state.entry(r0).or_insert(0) = alloc_base;
                            alloc_base += constant;
                        }
                        _ => unreachable!(),
                    }
                }
                // arithmetic handlers
                _ => {
                    *register_state.entry(r0).or_insert(0) = VMEmulator::eval_alu(
                        alu_semantics.get(&(alu_num as usize)).unwrap(),
                        v1,
                        v2,
                        constant,
                        key,
                    );
                }
            };

            // println!("{:?}", register_state[&r0]);
        }

        // print result
        // println!("vm: {:?}", register_state[&0]);
        register_state[&0]
    }

    fn eval_alu(expr: &LinearizedExpr, x: u64, y: u64, c: u64, k: u64) -> u64 {
        let symbols = VMEmulator::prepare_symbols();

        let mut symbolic_executor = SemanticFormulaEvaluator::new(symbols);

        symbolic_executor.eval_assignment(&Assignment::new(reg("x", 64), constant(x, 64)));
        symbolic_executor.eval_assignment(&Assignment::new(reg("y", 64), constant(y, 64)));
        symbolic_executor.eval_assignment(&Assignment::new(reg("c", 64), constant(c, 64)));
        symbolic_executor.eval_assignment(&Assignment::new(reg("k", 64), constant(k, 64)));

        symbolic_executor.eval_expression(expr).get_constant_val()
    }

    fn prepare_symbols() -> Vec<LinearExpr> {
        vec![reg("x", 64), reg("y", 64), reg("c", 64), reg("k", 64)]
            .into_iter()
            .flat_map(|s| s.gen_se_symbols().into_iter())
            .collect()
    }

    fn decode_instruction(instr_bytes: &[u8]) -> (u16, u16, u16, u16, u64, u64) {
        assert_eq!(instr_bytes.len(), 24);

        let alu_index = u16::from_le_bytes(instr_bytes[0..2].try_into().unwrap());
        let r0 = u16::from_le_bytes(instr_bytes[2..4].try_into().unwrap());
        let r1 = u16::from_le_bytes(instr_bytes[4..6].try_into().unwrap());
        let r2 = u16::from_le_bytes(instr_bytes[6..8].try_into().unwrap());
        let c = u64::from_le_bytes(instr_bytes[8..16].try_into().unwrap());
        let key = u64::from_le_bytes(instr_bytes[16..24].try_into().unwrap());

        (alu_index, r0, r1, r2, c, key)
    }
}

pub struct InputEmulator {}

impl InputEmulator {
    pub fn emulate(assignments: &Vec<Assignment>, constraints: &Vec<Assignment>) -> u64 {
        InputEmulator::symbolic_execute(&assignments, constraints)
    }

    fn symbolic_execute(assignments: &Vec<Assignment>, constraints: &Vec<Assignment>) -> u64 {
        // prepare symbols
        let symbols = InputEmulator::prepare_symbols(assignments);
        // get output var
        let output_var = assignments
            .last()
            .expect("Could not access output variable.")
            .lhs
            .clone();
        // init SE
        let mut symbolic_executor = SemanticFormulaEvaluator::new(symbols);

        /* contraint for concolic execution */
        for c in constraints {
            symbolic_executor.eval_assignment(c);
        }

        // init alloc
        let mut alloc_base = 0x800;

        // symbolic execution
        for assignment in assignments {
            // println!("before: {:?}", assignment);
            // println!("pretty: {}", assignment.to_string());

            // handle allocate
            match assignment.rhs.op().op {
                LinearExprOp::Alloc(c) => {
                    for index in 0..c {
                        let address = constant(alloc_base + index, 64).simplify();
                        let zero = constant(0, 8);
                        let assignment_ = Assignment::new(mem(address, 8), zero);
                        symbolic_executor.eval_assignment(&assignment_);
                    }
                    let assignment_ = Assignment::new(
                        assignment.lhs.clone(),
                        constant(alloc_base, assignment.size),
                    );
                    symbolic_executor.eval_assignment(&assignment_);

                    alloc_base += c;
                    continue;
                }
                _ => {}
            };

            // rewrite memory address on lhs: @[id.xxx] -> @[0x2222] and implement bytewise store
            match assignment.lhs.op().op == LinearExprOp::Mem {
                true => {
                    // rewrite memory
                    let address = assignment
                        .lhs
                        .get_expression_slice(0, assignment.lhs.len() - 1)
                        .simplify();
                    let address_val = symbolic_executor.symbolic_state.get_var(&address);
                    assert_eq!(address_val.size(), 64);
                    assert!(address_val.is_constant());

                    // bytewise store
                    for index in 0..(assignment.size / 8) {
                        let key = mem(
                            (address_val.clone() + constant(index as u64, address_val.size()))
                                .simplify(),
                            8,
                        );
                        let value = slice(
                            assignment.rhs.clone(),
                            (index as u8) * 8,
                            (index as u8) * 8 + 7,
                        )
                        .simplify();
                        let assignment_ = Assignment::new(key, value.clone());
                        // println!("{}", assignment_.to_string());
                        symbolic_executor.eval_assignment(&assignment_);
                    }
                    continue;
                }
                _ => {}
            }

            symbolic_executor.eval_assignment(&assignment);
        }

        // debug output
        // println!(
        //     "input: {:?}",
        //     symbolic_executor
        //         .symbolic_state
        //         .get_var(&output_var)
        //         .get_constant_val()
        // );

        symbolic_executor
            .symbolic_state
            .get_var(&output_var)
            .get_constant_val()
    }

    fn prepare_symbols(assignments: &Vec<Assignment>) -> Vec<LinearExpr> {
        assignments
            .iter()
            .flat_map(|ass| ass.lhs.gen_se_symbols())
            .chain(assignments.iter().flat_map(|ass| ass.rhs.gen_se_symbols()))
            .collect()
    }
}

pub struct Verificator {}

impl Verificator {
    pub fn verify_transformation(
        alu_semantics: &HashMap<usize, LinearizedExpr>,
        bytecode: &[u8],
        argument_keys: &Vec<u16>,
        input_data: &LLVMInputData,
        num_iter: usize,
    ) -> bool {
        (0..num_iter).into_par_iter().all(|_| {
            // get input arguments
            let input_arguments = Verificator::prepare_input_arguments(input_data);
            // generate random inputs
            let input_values: Vec<u64> = Verificator::prepare_rand_inputs(&input_arguments);
            // generate random memory bytes
            let memory_bytes = Verificator::prepare_rand_memory_bytes(input_arguments.len());
            // prepare for VM emulator
            let arguments = Verificator::prepare_vm_emulator(argument_keys, &input_values);
            // prepare for input emulator
            let constraints =
                Verificator::prepare_input_emulator(&input_arguments, &input_values, &memory_bytes);

            // check for equality
            let input_result =
                InputEmulator::emulate(&input_data.instructions_emulator, &constraints);
            let vm_result = VMEmulator::emulate(alu_semantics, bytecode, &arguments, &memory_bytes);
            if input_result == vm_result {
                return true;
            }
            println!(
                "Emulation found mismatch -- input: {} - vm: {}",
                input_result, vm_result
            );
            false
        })
    }

    fn prepare_input_arguments(input_data: &LLVMInputData) -> Vec<LinearizedExpr> {
        input_data
            .arguments
            .iter()
            .map(|name| {
                LinearizedExpr::from_linear_expr(
                    input_data
                        .instructions
                        .iter()
                        .flat_map(|a| a.rhs.0.iter())
                        .filter(|n| n.is_var())
                        .filter(|n| n.get_var_name() == name)
                        .nth(0)
                        .unwrap()
                        .clone(),
                )
            })
            .collect()
    }

    fn prepare_rand_inputs(input_arguments: &Vec<LinearizedExpr>) -> Vec<u64> {
        (0..input_arguments.iter().len())
            .map(|i| mask_to_size(thread_rng().gen::<u64>(), input_arguments[i].size()))
            .collect()
    }

    fn prepare_rand_memory_bytes(n: usize) -> HashMap<usize, Vec<u64>> {
        (0..n)
            .map(|i| {
                (
                    i,
                    (0..256)
                        .map(|_| mask_to_size(thread_rng().gen::<u64>(), 8))
                        .collect::<Vec<_>>(),
                )
            })
            .collect()
    }

    fn prepare_vm_emulator(argument_keys: &Vec<u16>, input_values: &Vec<u64>) -> Vec<(u16, u64)> {
        (0..input_values.len())
            .map(|i| (argument_keys[i], input_values[i]))
            .collect()
    }

    fn prepare_input_emulator(
        input_arguments: &Vec<LinearizedExpr>,
        input_values: &Vec<u64>,
        memory_bytes: &HashMap<usize, Vec<u64>>,
    ) -> Vec<Assignment> {
        // init
        let mut ret = vec![];

        // walk over all inputs
        for index in 0..input_arguments.len() {
            // prepare registers
            let lhs = input_arguments[index].clone();
            let base_address = constant(input_values[index], lhs.size());
            ret.push(Assignment::new(lhs, base_address.clone()));

            // prepare memory
            for offset in 0..memory_bytes[&index].len() {
                let address = add(
                    zero_extend(base_address.clone(), 64),
                    constant(offset as u64, 64),
                    64,
                )
                .simplify();
                let lhs = mem(address, 8);
                let rhs = constant(memory_bytes[&index][offset], 8);

                ret.push(Assignment::new(lhs, rhs));
            }
        }

        ret
    }
}
