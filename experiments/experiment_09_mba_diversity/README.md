# Experiment 9 MBA Diversity

We investigate the diversity of the (simplified) MBA. To this end, we re-use the same syntactic simplification binaries from experiment 6 to experiment 8.

You can use our experiment_09.py script or alternatively execute them individually.

## 1. Build Binaries

If you haven't run experiment 6, experiment 7, or expeirment 8 before, we need to build the binaries in a first step. These binaries will be used for *all* syntactic simplification experiments (i.e., taint analysis, slicing and SE). Instead of artifically trying to construct the handlers, we directly build them in our Rust tooling. To do so, we need to apply the [syntactic_simplification_binaries.patch](../../loki/obfuscator/syntactic_simplification_binaries.patch). Additionally, we need to disable in-built verification (using the `--verification-rounds 0` flag for `obfuscate.py`). We use the following configuration, which applies MBAs but avoid superoperators and indeterminism.

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


## 2. Run LokiAttack with MBA dumper plugin
In LokiAttack folder, we can then run the MBA dumper plugin:
```
python3 run.py mba_dump /home/user/evaluation/experiment_06_07_08_syntactic_simplification/binaries dynamic -o /home/user/evaluation/experiment_06_07_08_syntactic_simplification/mba_diversity_dynamic.txt
```

## 3. Draw conclusions
For the results file, we can analyze them:
```
python3 eval_mba_diversity.py /home/user/evaluation/experiment_06_07_08_syntactic_simplification/mba_diversity_dynamic.txt
```
This will print some statistics.


You can similarly create a second set of binaries, run LokiAttack with the MBA dumper plugin (take care to not overwrite the current results) and then diff these (assuming the `mba_diversity_dynamic_second_set.txt` holds the second set).

```
python3 eval_mba_diversity.py /home/user/evaluation/experiment_06_07_08_syntactic_simplification/mba_diversity_dynamic.txt --diff-to /home/user/evaluation/experiment_06_07_08_syntactic_simplification/mba_diversity_dynamic_second_set.txt 
```
