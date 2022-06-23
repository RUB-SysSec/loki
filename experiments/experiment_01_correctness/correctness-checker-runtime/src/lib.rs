use std::{env, fs::File, time::Instant};

use ctor::ctor;
use libc::c_void;
use serde::{Deserialize, Serialize};
use memmap::MmapOptions;

#[derive(Hash, Debug)]
struct Addresses {
    context: u64,
    vm_setup: u64,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct IOPair {
    input_1: Vec<u8>,
    input_2: Vec<u8>,
    output: u64,
}

// struct Context {
//     uint64_t regs[kRegCount];
//     void reset() { std::memset(regs, 0, kRegCount); }
//   };

#[repr(C)]
struct Context {
    regs: [u64; 65536],
    _reset: *const c_void,
}

impl Context {
    fn zero(&mut self) {
        self.regs.copy_from_slice(&[0u64; 65536])
    }
}

// #[ctor]
// fn obf_exe_checker() {
//     println!("Correctness-Checker going online");

//     // let arg1 = CString::new("A").unwrap();
//     // let arg2 = CString::new("A").unwrap();

//     let mut arg3 = [0x41u8; 129];
//     arg3[128] = 0x00;

//     let vm_args = [arg3.as_ptr() as *const i8, arg3.as_ptr() as *const i8];
//     let context_ptr: u64 = 0x661740;
//     let context_ptr = context_ptr as *const Context as *mut Context;
//     let virtual_address: u64 = 0x40a5c0;
//     let ptr = virtual_address as *const ();
//     let code: extern "C" fn(*const *const i8, *const Context, u64) =
//         unsafe { std::mem::transmute(ptr) };

//     let context = unsafe { &mut *context_ptr };
//     context.zero();

//     // let start = Instant::now();
//     let execs = 10; // 15_000;
//     for _ in 0..execs {
//         // (code)(vm_args.as_ptr(), context, 0);
//         (code)(vm_args.as_ptr(), context, 0);
//         let output = context.regs[0];
//         println!("output={}", output);
//         // let vip = context.regs[1];
//         // let reg = context.regs[2];
//         // println!("output={}, vip={:#x}, reg1={:#x}", output, vip, reg);
//     }
//     unsafe {
//         let x = ptr::read_unaligned(context_ptr as *const [u64; 4]);
//         println!("x={:x?}", x);
//     }
//     // let time = start.elapsed();
//     // println!("time={:?}, execs/s={:?}", time, execs / time.as_secs());

//     println!("Correctness-Checker done");
// }

fn execute_vm(addr_context: u64, addr_vm_setup: u64, io_pair: &IOPair) -> u64 {
    let vm_args = [
        io_pair.input_1.as_ptr() as *const i8,
        io_pair.input_2.as_ptr() as *const i8,
    ];
    let context_ptr = addr_context as *const Context as *mut Context;
    let ptr = addr_vm_setup as *const ();
    let code: extern "sysv64" fn(*const *const i8, *const Context, u64) =
        unsafe { std::mem::transmute(ptr) };

    let context = unsafe { &mut *context_ptr };
    context.zero();

    (code)(vm_args.as_ptr(), context, 0);
    let output = context.regs[0];
    if output != io_pair.output {
        println!(
            "CHECKER: ERROR: Mismatch -- {:?} {:?} -> {} (expected {})",
            io_pair.input_1, io_pair.input_2, output, io_pair.output
        );
        return 1;
    }

    0
}

#[ctor]
fn obf_exe_checker() {
    let start = Instant::now();
    println!("CHECKER: going online");

    println!("CHECKER: Reading environment variables..");
    let inputs_file =
        env::var("CHECKER_INPUTS_FILE").expect("CHECKER: CHECKER_INPUTS_FILE env var not set");
    let testcase = env::var("CHECKER_TC_NAME").expect("CHECKER: CHECKER_TC_NAME env var not set");
    let addr_context: u64 = env::var("CHECKER_ADDRESS_CONTEXT")
        .expect("CHECKER: CHECKER_ADDRESS_CONTEXT env var not set")
        .parse()
        .expect("CHECKER: Failed to parse CHECKER_ADDRESS_CONTEXT");
    let addr_vm_setup: u64 = env::var("CHECKER_ADDRESS_VM_SETUP")
        .expect("CHECKER: CHECKER_ADDRESS_VM_SETUP env var not set")
        .parse()
        .expect("CHECKER: Failed to parse CHECKER_ADDRESS_VM_SETUP");

    println!(
        "CHECKER: Testing {}; reading inputs from {}; context address: {:#x}; vm setup address: {:#x}",
        &testcase, &inputs_file, addr_context, addr_vm_setup
    );

    println!("CHECKER: Loading inputs from {}..", &inputs_file);

    // avoid loading all data but parse line-by-line to keep memory consumption low
    let file = File::open(&inputs_file).expect("CHECKER: Unable to read inputs file");
    let mmap = unsafe { MmapOptions::new().map(&file).expect("CHECKER: Failed to mmap inputs file") };

    let mut failure_ctr = 0;
    let mut length: u64 = 0;
    let mut mmap_iter = mmap.iter();
    loop {
        let mut data: Vec<u8> = Vec::new();

        while let Some(c) = mmap_iter.next() {
            // break on newline
            if *c == 10 {
                break;
            }
            data.push(*c);
        }

        if data.is_empty() {
            break;
        }

        let string = String::from_utf8(data).expect("CHECKER: Failed to parse line");
        let io_pair: IOPair = serde_json::from_str(&string).expect("CHECKER: Unable to parse inputs file");
        failure_ctr += execute_vm(addr_context, addr_vm_setup, &io_pair);
        length += 1;

        if length % 100_000 == 0 {
            println!("CHECKER: Processing.. {} entries done", length);
        }
    }

    let runtime = start.elapsed();
    println!(
        "CHECKER: Done in {:?} -- {} / {} failed",
        runtime, failure_ctr, length
    );

    unsafe {
        libc::exit(0);
    }
}
