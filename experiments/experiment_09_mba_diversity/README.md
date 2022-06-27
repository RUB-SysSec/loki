# Experiment 9 MBA Diversity

We investigate the diversity of the (simplified) MBA. To this end, we re-use the same syntactic simplification binaries from experiment 6 to experiment 8.

You can use our experiment_09.py script _(expected runtime: 5 minutes)_ or alternatively execute them individually.

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
git checkout .
git apply syntactic_simplification_binaries.patch
# build patched binary
cargo build --release

# create binaries
cd ..
mkdir -p /home/user/evaluation/experiment_06_07_08_syntactic_simplification
python3 obfuscate.py /home/user/evaluation/experiment_06_07_08_syntactic_simplification/binaries --instances 10 --allow se_analysis --verification-rounds 0 --nosuperopt --deterministic
# create a second set of binaries
python3 obfuscate.py /home/user/evaluation/experiment_06_07_08_syntactic_simplification/binaries_second_set --instances 10 --allow se_analysis --verification-rounds 0 --nosuperopt --deterministic

# undo patch
cd obfuscator
git checkout .
cd ../../experiments/experiment_09_mba_diversity
```
_Expected time (104 CPU cores): ~5 minutes_

To speedup this process, we only create 10 instances instead of 1,000 as in the paper.


## 2. Run LokiAttack with MBA dumper plugin
In LokiAttack folder, we can then run the MBA dumper plugin:
```
cd ../../lokiattack

python3 run.py mba_dump /home/user/evaluation/experiment_06_07_08_syntactic_simplification/binaries dynamic -o /home/user/evaluation/experiment_06_07_08_syntactic_simplification/mba_diversity_first_set.txt

python3 run.py mba_dump /home/user/evaluation/experiment_06_07_08_syntactic_simplification/binaries_second_set dynamic -o /home/user/evaluation/experiment_06_07_08_syntactic_simplification/mba_diversity_second_set.txt

cd -
```
_Expected time (104 CPU cores): ~5 seconds_

## 3. Draw conclusions
For the results file, we can analyze them:
```
python3 eval_mba_diversity.py /home/user/evaluation/experiment_06_07_08_syntactic_simplification/mba_diversity_first_set.txt
```
This will print some statistics.


Optionally, you can similarly create a second set of binaries, run LokiAttack with the MBA dumper plugin (take care to not overwrite the current results) and then diff these (assuming the `mba_diversity_second_set.txt` holds the second set).

```
python3 eval_mba_diversity.py /home/user/evaluation/experiment_06_07_08_syntactic_simplification/mba_diversity_first_set.txt --diff-to /home/user/evaluation/experiment_06_07_08_syntactic_simplification/mba_diversity_second_set.txt 
```
_Expected time (104 CPU cores): ~5 seconds_

You can compare the resulting percentage to the ones reported in Experiment 9 in the paper. Due to the lower number of instances used for this experiment (10, each having 7 handler => 70) compared to the paper (1,000, each having 7 handler => 7,000), the percentage of unique MBAs should be higher than in the paper.
