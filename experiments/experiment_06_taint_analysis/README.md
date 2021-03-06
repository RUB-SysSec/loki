# Experiment 6 Taint Analysis

This experiment requires 3 steps. You can use our experiment_06.py script _(expected runtime ~2.5h)_ or alternatively execute them individually. Before you can use Triton-based taint analysis, you need to install Triton -- run [../../lokiattack/install_triton.sh](../../lokiattack/install_triton.sh)

## 1. Build Binaries
First, we need to build binaries. These binaries will be used for *all* syntactic simplification experiments (i.e., backwards slicing and SE). Instead of artifically trying to construct the handlers, we directly build them in our Rust tooling. To do so, we need to apply the [syntactic_simplification_binaries.patch](../../loki/obfuscator/syntactic_simplification_binaries.patch). Additionally, we need to disable in-built verification (using the `--verification-rounds 0` flag for `obfuscate.py`). We use the following configuration, which applies MBAs but avoid superoperators and indeterminism.

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

# undo patch
cd obfuscator
git checkout .
cd ../../experiments/experiment_06_taint_analysis
```

_Expected time (104 CPU cores): ~2 minutes_

## 2. Run LokiAttack with taint analysis plugins
In LokiAttack folder, we can then run the bit-granular taint analysis based on Miasm and the byte-granular analysis based on Triton -- note that we run both twice, once for a static attacker and once for a dynamic attacker knowing the correct key:
```
cd ../../lokiattack

# Triton + static attacker -- expected runtime: 1 hour (due to a couple of timeouts)
python3 run.py taint_byte /home/user/evaluation/experiment_06_07_08_syntactic_simplification/binaries static -o /home/user/evaluation/experiment_06_07_08_syntactic_simplification/taint_analysis_triton_byte_level_static.txt

# Triton + dynamic attacker -- expected runtime: ~15 minutes
python3 run.py taint_byte /home/user/evaluation/experiment_06_07_08_syntactic_simplification/binaries dynamic -o /home/user/evaluation/experiment_06_07_08_syntactic_simplification/taint_analysis_triton_byte_level_dynamic.txt

# Miasm + static attacker -- expected runtime: 1 hour (due to a couple of timeouts)
python3 run.py taint_bit /home/user/evaluation/experiment_06_07_08_syntactic_simplification/binaries static -o /home/user/evaluation/experiment_06_07_08_syntactic_simplification/taint_analysis_miasm_bit_level_static.txt

# Miasm + dynamic attacker -- expected runtime: ~15 minutes 
python3 run.py taint_bit /home/user/evaluation/experiment_06_07_08_syntactic_simplification/binaries dynamic -o /home/user/evaluation/experiment_06_07_08_syntactic_simplification/taint_analysis_miasm_bit_level_dynamic.txt

cd -
```
_Expected time (104 CPU cores): 2.5 hours_

## 3. Draw conclusions
For each of the four results files, we can analyze them:
```
# Triton + static attacker
python3 eval_taint_analysis.py /home/user/evaluation/experiment_06_07_08_syntactic_simplification/taint_analysis_triton_byte_level_static.txt

# Triton + dynamic attacker
python3 eval_taint_analysis.py /home/user/evaluation/experiment_06_07_08_syntactic_simplification/taint_analysis_triton_byte_level_dynamic.txt

# Miasm + dynamic attacker
python3 eval_taint_analysis.py /home/user/evaluation/experiment_06_07_08_syntactic_simplification/taint_analysis_miasm_bit_level_static.txt

# Miasm + dynamic attacker
python3 eval_taint_analysis.py /home/user/evaluation/experiment_06_07_08_syntactic_simplification/taint_analysis_miasm_bit_level_dynamic.txt
```
_Expected time (104 CPU cores): 30 seconds_

This will print some statistics. The average number of IR paths, average time, and percentage of unmarked ("un-tainted") instructions can be compared to the numbers reported in Table 3, page 11, in our paper.
