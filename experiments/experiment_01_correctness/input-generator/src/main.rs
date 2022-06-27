use std::fs::File;
use std::io::prelude::*;

use itertools::Itertools;
use rand::distributions::Uniform;
use rand::prelude::Distribution;
use serde::{Deserialize, Serialize};

// const NUM_RANDOM_INPUTS_PER_LENGTH_LEVEL: usize = 10_000;
const NUM_RANDOM_INPUTS_PER_LENGTH_LEVEL: usize = 1_000;
const LENGTH_LEVEL_UPPER_BOUND: usize = 128 + 1;
const LENGTH_LEVEL_LOWER_BOUND: usize = 16;
const INPUT_LEN: usize = 128;
const EDGE_CASES_BYTES: [u8; 4] = [0x00, 0xff, 0xaa, 0x55];

#[derive(Debug, Serialize, Deserialize)]
pub struct InputTuple {
    input_1: Vec<u8>,
    input_2: Vec<u8>,
    output: Option<u64>,
}

impl InputTuple {
    fn new(input_1: Vec<u8>, input_2: Vec<u8>, output: Option<u64>) -> InputTuple {
        InputTuple {
            input_1,
            input_2,
            output,
        }
    }
}

fn gen_edge_cases(length: usize) -> Vec<Vec<u8>> {
    let mut edge_cases = Vec::new();
    for edge_case_byte in EDGE_CASES_BYTES {
        edge_cases.push(vec![edge_case_byte; length]);
    }
    // leading bit set to 1
    let mut edge_case: Vec<u8> = vec![0x80u8];
    edge_case.extend(vec![0x00u8; length - 1]);
    edge_cases.push(edge_case);

    // last bit set to 1
    let mut edge_case: Vec<u8> = vec![0x00];
    edge_case.push(0x01);
    edge_cases.push(edge_case);

    edge_cases
}

fn edge_case_combinations(edge_cases: Vec<Vec<u8>>) -> Vec<(Vec<u8>, Vec<u8>)> {
    edge_cases
        .clone()
        .into_iter()
        .cartesian_product(edge_cases.into_iter())
        .collect_vec()
}

fn main() {
    let lvls = LENGTH_LEVEL_UPPER_BOUND - LENGTH_LEVEL_LOWER_BOUND;
    let total_random = NUM_RANDOM_INPUTS_PER_LENGTH_LEVEL * lvls;
    let total_det = gen_edge_cases(128).len().pow(2) * lvls;
    let total = total_random + total_det;
    println!(
        "Generating {} inputs in total ({} edge cases and {} random inputs)..",
        total, total_det, total_random
    );

    let between = Uniform::from(0x0u8..0xffu8);
    let mut rng = rand::thread_rng();

    let mut input_tuples = Vec::new();

    for input_length in LENGTH_LEVEL_LOWER_BOUND..LENGTH_LEVEL_UPPER_BOUND {
        let edge_cases = edge_case_combinations(gen_edge_cases(input_length));

        // Generate edge cases
        for (input_1, input_2) in edge_cases {
            let mut padded_input_1 = vec![0x00u8; 128 - input_1.len()];
            padded_input_1.extend(input_1);
            let mut padded_input_2 = vec![0x00u8; 128 - input_2.len()];
            padded_input_2.extend(input_2);
            input_tuples.push(InputTuple::new(padded_input_1, padded_input_2, None));
        }
        // Generate random inputs
        for _ in 0..NUM_RANDOM_INPUTS_PER_LENGTH_LEVEL {
            let input_1: Vec<u8> = between.sample_iter(&mut rng).take(input_length).collect();
            let input_2: Vec<u8> = between.sample_iter(&mut rng).take(input_length).collect();
            let mut padded_input_1 = vec![0x00u8; INPUT_LEN - input_1.len()];
            padded_input_1.extend(input_1);
            let mut padded_input_2 = vec![0x00u8; INPUT_LEN - input_2.len()];
            padded_input_2.extend(input_2);
            input_tuples.push(InputTuple::new(padded_input_1, padded_input_2, None));
        }
    }

    let data = serde_json::to_string(&input_tuples).unwrap();
    let mut file = File::create("inputs.json").expect("Failed to create inputs.json file");
    file.write_all(data.as_bytes())
        .expect("Failed to write to inputs.json file");
    println!("Done generating inputs!")
}
