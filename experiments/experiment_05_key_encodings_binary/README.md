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
mkdir -p /home/user/evaluation/experiment_05_key_encodings_bin_level/
./obfuscate.py /home/user/evaluation/experiment_05_key_encodings_bin_level/binaries --instances 1000 --allow smt_analysis --nomba --nosuperopt --deterministic
```

## 2. Run LokiAttack with SMT solver plugin
In LokiAttack folder, run:
```
mkdir -p ~/evaluation/experiment_data
python3 run.py smt  /home/user/evaluation/experiment_05_key_encodings_bin_level/binaries static -o /home/user/evaluation/experiment_05_key_encodings_bin_level/results.txt
```

## 3. Draw conclusions
```
python3 eval_smt.py /home/user/evaluation/experiment_05_key_encodings_bin_level/results.txt
```
This will evaluate the results and print some statistics.
