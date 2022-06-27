# Experiment 4 Hardness of Key Encodings

The tooling needed for this experiment is included within our Rust component, VM_ALU. More precisely, it is at [vm_alu/src/eval_tools/smt.rs](../../loki/obfuscator/vm_alu/src/eval_tools/smt.rs).

To conduct this experiment, run:
```
python3 experiment_04.py --num-encodings 10
```
Note that this evaluates 10 encodings for both the factorization encoding and point function encoding (in our paper, we use 1,000).

You should see that the SMT solver solved 0 of the factorization encodings, while it solves about 7 of the point functions (given the low number of samples, the number of solves may vary for point functions -- you can increase the sample size if necessary).

_Expected time (104 CPU cores): ~3 hours_

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
