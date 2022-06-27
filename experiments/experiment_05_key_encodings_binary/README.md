# Experiment 5 Key Encodings on the Binary Level

This experiment requires 3 steps. You can use our experiment_05.py script or alternatively execute them individually.

## 1. Build Binaries
First, we need to build binaries with the following Rust component config:

```
# Settings:
    rewrite_mba: false,
    superoptimization: false,
    schedule_non_deterministic: false,
```
This does not apply MBAs or superoperators and schedules the VM handler deterministically (such that we have a ground truth for the evaluation).

To do so, run the following: 

```
cd ../../loki/
mkdir -p /home/user/evaluation/experiment_05_key_encodings_bin_level/
python3 obfuscate.py /home/user/evaluation/experiment_05_key_encodings_bin_level/binaries --instances 20 --allow smt_analysis --nomba --nosuperopt --deterministic
cd -
```
_Expected time (104 CPU cores): 2 minutes_

Note that contrary to the paper, we build 20 instances instead of 1,000.


## 2. Run LokiAttack with SMT solver plugin
In LokiAttack folder, run:
```
cd ../../lokiattack
python3 run.py smt /home/user/evaluation/experiment_05_key_encodings_bin_level/binaries static -o /home/user/evaluation/experiment_05_key_encodings_bin_level/results.txt
cd -
```
_Expected time (104 CPU cores): 4 hours_

If this runtime is deemed excessive, we recommend creating only 10 obfuscated instances instead of 20.

## 3. Draw conclusions
```
python3 eval_smt.py /home/user/evaluation/experiment_05_key_encodings_bin_level/results.txt
```
_Expected time (104 CPU cores): 1 second_

This will evaluate the results and print some statistics. You can compare the percentage where z3 managed to find a correct key ("solved") to the number reported in the Expeirment 5 in the paper.
