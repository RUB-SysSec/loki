# Experiment 4 Hardness of Key Encodings

The tooling needed for this experiment is included within our Rust component, VM_ALU. More precisely, it is at [vm_alu/src/eval_tools/smt.rs](../../loki/obfuscator/vm_alu/src/eval_tools/smt.rs).

Either run experiment_04.py or follow the following steps:

## Generate Key Encodings
In [loki/obfuscator](../../loki/obfuscator) directory, run:
```
# create one factorization encoding
cargo run --release --bin eval_smt factorization

# create one pointfunction encoding
cargo run --release --bin eval_smt pointfunction
```

You need to run these commands N times to produce N formulas and redirect the output into a file to store it.

## CEGAR
For each encoding file you created, run [solve.py](./solve.py):
```
python3 solve.py PATH_TO_FILE
```
