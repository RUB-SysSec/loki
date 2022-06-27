# Experiment 11 Complexity of Core Semantics

We investigate the complexity of our core semantics in terms of their semantic depth. We use a special branch of our Rust obfuscator component to create binaries of depth 3 and 5, which will output a file containing this data.

You can use our experiment_11.py script or alternatively the following steps individually.

## 1. Generate data

Instead of building binaries, we use the [core_semantics_complexity.patch](../../loki/obfuscator/core_semantics_complexity.patch) to generate files called superhandler_data.txt, which contains the necessary data.
We set the flag `--no-generate-vm` to avoid trying to compile binaries (which will not work as we do produce only superhandler_data.txt data)

```
# Settings:
    rewrite_mba: false,
    superoptimization: false,
```

To build the binaries, run the following: 

```
# apply patch
cd ../../loki/obfuscator
git checkout .
git apply core_semantics_complexity.patch
# build patched binary
cargo build --release
cd ..

# create binaries
mkdir -p /home/user/evaluation/experiment_11_complexity_of_core_semantics
# first set without superoperators
python3 obfuscate.py /home/user/evaluation/experiment_11_complexity_of_core_semantics/binaries_no_superoperator --instances 10 --allow aes_encrypt des_encrypt md5 sha1 rc4 --verification-rounds 0 --no-generate-vm --nomba --nosuperopt

# second set with superoperators
python3 obfuscate.py /home/user/evaluation/experiment_11_complexity_of_core_semantics/binaries_with_superoperator --instances 10 --allow aes_encrypt des_encrypt md5 sha1 rc4 --verification-rounds 0 --no-generate-vm --nomba

# undo patch
cd obfuscator
git checkout .
cd ../../experiments/experiment_11_core_semantics_complexity
```
_Expected time (104 CPU cores): 5 minutes_

## 2. Run Experiment
We can then run the eval_complexity script with the two directories containing data for when *not* using superoperators and when using superoperators:
```
python3 eval_complexity.py /home/user/evaluation/experiment_11_complexity_of_core_semantics/binaries_no_superoperator /home/user/evaluation/experiment_11_complexity_of_core_semantics/binaries_with_superoperator

```
_Expected time (104 CPU cores): 1 second_

This will print some statistics (and sort-of an ASCII figure). You can compare these values to Figure 4, page 14, "Complexity of Generated Handlers" in our paper. While individual shapes may vary, the interesting aspect is that without superoperators, the highest observable is 5 (with peaks at depth 3 and depth 5), while our superoperators move the spectrum to higher depths (with the hightest peak at depth 9).

Alternatively, you can create a plot:
```
python3 plot_complexity.py complexity_data.txt
```
