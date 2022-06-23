# Experiment 8 Symbolic Execution

This experiment has two dimensions: We repeat it for the same binaries (with core semantics of semantic depth 3) as in experiment 6 and experiment 7. Then, we create new binaries where the core semantics have depth 5. Each of them requires 3 steps. We first run the experiment for depth 3, then for depth 5.

You can use our experiment_08.py script or alternatively execute them individually.

## 1. Build Binaries

We do this first for depth 3, then depth 5.

### Depth 3

If you haven't run experiment 6 or experiment 7 before, we need to build the binaries of depth 3 in a first step. These binaries will be used for *all* syntactic simplification experiments (i.e., taint analysis, slicing and SE). Instead of artifically trying to construct the handlers, we directly build them in our Rust tooling. To do so, we need to apply the [syntactic_simplification_binaries.patch](../../loki/obfuscator/syntactic_simplification_binaries.patch). Additionally, we need to disable in-built verification (using the `--verification-rounds 0` flag for `obfuscate.py`). We use the following configuration, which applies MBAs but avoid superoperators and indeterminism.

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

### Depth 5

Again, we directly build these binaries in our Rust tooling. To do so, we need to apply the [syntactic_simplification_binaries_depth_5.patch](../../loki/obfuscator/syntactic_simplification_binaries_depth_5.patch) (notice the depth_5 suffix). Additionally, we need to disable in-built verification (using the `--verification-rounds 0` flag for `obfuscate.py`). We use the following configuration, which applies MBAs but avoid superoperators and indeterminism.

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
git apply syntactic_simplification_binaries_depth_5.patch
# build patched binary
cargo build --release

# create binaries
cd -
mkdir -p /home/user/evaluation/experiment_06_07_08_syntactic_simplification
./obfuscate.py /home/user/evaluation/experiment_06_07_08_syntactic_simplification/binaries_depth_5 --instances 1000 --allow se_analysis --verification-rounds 0 --nosuperopt --deterministic

# undo patch
cd ../../loki/obfuscator
git checkout .
cd -
```

## 2. Run LokiAttack with symbolic execution plugins
In LokiAttack folder, we can then run the symbolic execution plugin (for both sets of binaries) -- note that we run it twice for each set, once for a static attacker and once for a dynamic attacker knowing the correct key:
```
# depth 3 + static attacker
python3 run.py se /home/user/evaluation/experiment_06_07_08_syntactic_simplification/binaries static -o /home/user/evaluation/experiment_06_07_08_syntactic_simplification/symbolic_execution_static.txt

# depth 3 + dynamic attacker
python3 run.py se /home/user/evaluation/experiment_06_07_08_syntactic_simplification/binaries dynamic -o /home/user/evaluation/experiment_06_07_08_syntactic_simplification/symbolic_execution_dynamic.txt

# depth 5 + static attacker
python3 run.py se_depth5 /home/user/evaluation/experiment_06_07_08_syntactic_simplification/binaries_depth_5 static -o /home/user/evaluation/experiment_06_07_08_syntactic_simplification/symbolic_execution_depth_5_static.txt

# depth 5 + dynamic attacker
python3 run.py se_depth5 /home/user/evaluation/experiment_06_07_08_syntactic_simplification/binaries_depth_5 dynamic -o /home/user/evaluation/experiment_06_07_08_syntactic_simplification/symbolic_execution_depth_5_dynamic.txt
```

## 3. Draw conclusions
For each of the four results files, we can analyze them:
```
# depth 3 + static attacker
python3 eval_backward_slicing.py /home/user/evaluation/experiment_06_07_08_syntactic_simplification/symbolic_execution_static.txt

# depth 3 dynamic attacker
python3 eval_backward_slicing.py /home/user/evaluation/experiment_06_07_08_syntactic_simplification/symbolic_execution_dynamic.txt

# depth 5 + static attacker
python3 eval_backward_slicing.py /home/user/evaluation/experiment_06_07_08_syntactic_simplification/symbolic_execution_depth_5_static.txt

# depth 5 dynamic attacker
python3 eval_backward_slicing.py /home/user/evaluation/experiment_06_07_08_syntactic_simplification/symbolic_execution_depth_5_dynamic.txt
```
This will print some statistics.
