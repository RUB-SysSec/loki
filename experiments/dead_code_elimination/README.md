# Deadcode Elimination

While not an experiment in our evaluation, we have shown in Table 1 of our paper that deadcode elimination (or more general compiler optimizations) are a powerful tool, however, fall short w.r.t. to our design, Loki.

To conduct this experiment, use experiment_dce.py (which builds 10 binaries and samples 1000 handlers) or follow the subsequent steps:


## 1. Build Binaries
First, we need to build binaries with the following Rust component config:

```
# Settings:
    rewrite_mba: true,
    superoptimization: true,
    schedule_non_deterministic: true,
```

To do so, run the following: 

```
mkdir -p /home/user/evaluation/experiment_01_02_03_dce/
./obfuscate.py /home/user/evaluation/experiment_01_02_03_dce/binaries --instances 1000 --allow aes_encrypt des_encrypt md5 rc4 sha1
```

## 2. Extract handler addresses

First, extract all handler and their addresses - to do so, switch to the [../../lokiattack](../../lokiattack) folder and run:
```
python3 extract_handler_addresses.py /home/user/evaluation/experiment_01_02_03_dce/binaries -o /home/user/evaluation/experiment_01_02_03_dce/dce_handler_addresses.txt
```

## 3. Run dead code eliminiation

Then, run the dead code elimination (again in the lokiattack directory):
```
python3 compiler_optimizations.py /home/user/evaluation/experiment_01_02_03_dce/dce_handler_addresses.txt -o /home/user/evaluation/experiment_01_02_03_dce/dce_results.txt
```

## 4. Evaluate results

Finally, evaluate the results using `eval_dead_code_elimination.py` in this directory:

```
python3 eval_dead_code_elimination.py /home/user/evaluation/experiment_01_02_03_dce/dce_results.txt
```
