# Experiment 7 Backward Slicing

This experiment requires 3 steps (and works on the same binaries as experiment 6 and experiment 8). You can use our experiment_07.py script or alternatively execute them individually.

## 1. Build Binaries
If you haven't run experiment 6 before, we need to build the binaries in a first step. These binaries will be used for *all* syntactic simplification experiments (i.e., taint analysis, slicing and SE). Instead of artifically trying to construct the handlers, we directly build them in our Rust tooling. To do so, we need to apply the [syntactic_simplification_binaries.patch](../../loki/obfuscator/syntactic_simplification_binaries.patch). Additionally, we need to disable in-built verification (using the `--verification-rounds 0` flag for `obfuscate.py`). We use the following configuration, which applies MBAs but avoid superoperators and indeterminism.

```
# Settings:
    rewrite_mba: true,
    superoptimization: false,
    schedule_non_deterministic: false,
```

To build the binaries, run the following: 

```
# apply patch
cd ../../loki/obfuscator
git apply syntactic_simplification_binaries.patch
# build patched binary
cargo build --release

# create binaries
cd -
mkdir -p /home/user/evaluation/experiment_06_07_08_syntactic_simplification
./obfuscate.py /home/user/evaluation/experiment_06_07_08_syntactic_simplification/binaries --instances 1000 --allow se_analysis --verification-rounds 0 --nosuperopt --deterministic

# undo patch
cd ../../loki/obfuscator
git checkout .
cd -
```

## 2. Run LokiAttack with backward slicing plugin
In LokiAttack folder, we can then run the backward slicing plugin -- note that we run it twice, once for a static attacker and once for a dynamic attacker knowing the correct key:
```
# static attacker
python3 run.py backward_slicing /home/user/evaluation/experiment_06_07_08_syntactic_simplification/binaries static -o /home/user/evaluation/experiment_06_07_08_syntactic_simplification/backward_slicing_static.txt

# dynamic attacker
python3 run.py backward_slicing /home/user/evaluation/experiment_06_07_08_syntactic_simplification/binaries dynamic -o /home/user/evaluation/experiment_06_07_08_syntactic_simplification/backward_slicing_dynamic.txt
```

## 3. Draw conclusions
For each of the two results files, we can analyze them:
```
# static attacker
python3 eval_backward_slicing.py /home/user/evaluation/experiment_06_07_08_syntactic_simplification/backward_slicing_static.txt

# dynamic attacker
python3 eval_backward_slicing.py /home/user/evaluation/experiment_06_07_08_syntactic_simplification/backward_slicing_dynamic.txt
```
This will print some statistics.
