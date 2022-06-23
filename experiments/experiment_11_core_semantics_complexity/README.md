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
git apply core_semantics_complexity.patch
# build patched binary
cargo build --release

# create binaries
cd -
mkdir -p /home/user/evaluation/experiment_11_complexity_of_core_semantics
# first set without superoperators
./obfuscate.py /home/user/evaluation/experiment_11_complexity_of_core_semantics/binaries_no_superoperator --instances 1000 --allow aes_
encrypt des_encrypt md5 sha1 rc4 --verification-rounds 0 --no-generate-vm --nomba --nosuperopt

# second set with superoperators
./obfuscate.py /home/user/evaluation/experiment_11_complexity_of_core_semantics/binaries_no_superoperator --instances 1000 --allow aes_
encrypt des_encrypt md5 sha1 rc4 --verification-rounds 0 --no-generate-vm --nomba

# undo patch
cd ../../loki/obfuscator
git checkout .
cd -
```


## 2. Run Experiment
We can then run the eval_complexity script with the two directories containing data for when *not* using superoperators and when using superoperators:
```
python3 eval_complexity.py /home/user/evaluation/experiment_11_complexity_of_core_semantics/binaries_no_superoperator /home/user/evaluation/experiment_11_complexity_of_core_semantics/binaries_with_superoperator

```
This will also directly print some statistics (and sort-of an ASCII figure).
