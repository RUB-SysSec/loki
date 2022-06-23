use std::{
    env,
    fs::{self, File},
    io::Write,
    time::Instant,
};

use ctor::ctor;
use serde::{Deserialize, Serialize};

#[derive(Debug, Serialize, Deserialize)]
pub struct IOPair {
    input_1: Vec<u8>,
    input_2: Vec<u8>,
    output: Option<u64>,
}

fn execute_target_function(target_function_address: u64, input: &IOPair) -> u64 {
    // let virtual_address: u64 = 0x400590;
    let ptr = target_function_address as *const ();
    let code: extern "sysv64" fn(*const i8, *const i8) -> u64 = unsafe { std::mem::transmute(ptr) };

    (code)(
        input.input_1.as_ptr() as *const i8,
        input.input_2.as_ptr() as *const i8,
    )
}

// checker for orig_exe
#[ctor]
fn input_oracle_ctor() {
    let start = Instant::now();
    println!("ORACLE: Evaluating inputs..");

    println!("ORACLE: Reading environment variables..");
    let inputs_file =
        env::var("ORACLE_INPUTS_FILE").expect("ORACLE: ORACLE_INPUTS_FILE env var not set");
    let output_file =
        env::var("ORACLE_OUTPUT_FILE").expect("ORACLE: ORACLE_OUTPUT_FILE env var not set");
    let testcase = env::var("ORACLE_TC_NAME").expect("ORACLE: ORACLE_TC_NAME env var not set");
    let addr_target_function: u64 = env::var("ORACLE_ADDRESS_TARGET_FUNCTION")
        .expect("ORACLE: ORACLE_ADDRESS_TARGET_FUNCTION env var not set")
        .parse()
        .expect("ORACLE: Failed to parse ORACLE_ADDRESS_TARGET_FUNCTION");

    println!(
        "ORACLE: Testing {}; reading inputs from {} and storing data to {}",
        &testcase, &inputs_file, &output_file
    );

    println!("ORACLE: Loading inputs from {}..", &inputs_file);

    let data = fs::read_to_string(&inputs_file).expect("ORACLE: Unable to read inputs.json file");
    let mut inputs: Vec<IOPair> =
        serde_json::from_str(&data).expect("ORACLE: Unable to parse inputs.json file");

    let length = &inputs.len();
    println!("ORACLE: Evaluating {} inputs..", length);
    for (i, io_pair) in inputs.iter_mut().enumerate() {
        let output = execute_target_function(addr_target_function, io_pair);

        io_pair.output = Some(output);

        if i % 100_000 == 0 {
            println!("ORACLE: Processing.. {}/{}", i, length)
        }
    }

    println!("ORACLE: Running sanity checks and writing data..");

    let mut file = File::create(output_file).expect("ORACLE: Failed to create output file");
    for io_pair in inputs.iter() {
        // sanity check
        assert!(io_pair.output.is_some());
        // write io_pair into a single line
        let data = serde_json::to_string(&io_pair).unwrap() + "\n";
        file.write_all(data.as_bytes())
        .expect("ORACLE: Failed to write to output file");
    }

    let runtime = start.elapsed();
    println!(
        "ORACLE: Done in {:?} -- {} inputs generated",
        runtime, length
    );

    unsafe {
        libc::exit(0);
    }
}

// // checker for orig_exe
// #[no_mangle]
// #[ctor]
// fn orig() {
//     println!("Correctness-Checker going online");

//     let arg1 = CString::new("A").unwrap();
//     let arg2 = CString::new("A").unwrap();

//     let mut arg3 = [0x41u8; 129];
//     arg3[128] = 0x00;
//     // arg3[10] = 0x41;
//     // arg3[11] = 0x00;
//     // arg3[12] = 0x41;
//     // arg3[30] = 0x42;
//     // arg3[31] = 0x00;
//     // arg3[32] = 0x42;

//     let virtual_address: u64 = 0x400590;
//     let ptr = virtual_address as *const ();
//     let code: extern "sysv64" fn(*const i8, *const i8) -> u64 = unsafe { std::mem::transmute(ptr) };

//     let execs = 10; // 15_000;
//     for _ in 0..execs {
//         // let output = (code)(arg1.as_ptr(), arg2.as_ptr());
//         unsafe {
//             let output = (code)(arg3.as_ptr() as *const i8, arg3.as_ptr() as *const i8);

//             println!("output={:?}", output);
//         }
//     }

//     println!("Correctness-Checker done");
// }
