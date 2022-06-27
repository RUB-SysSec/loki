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
cd ../../loki/
mkdir -p /home/user/evaluation/experiment_01_02_03_dce/
python3 obfuscate.py /home/user/evaluation/experiment_01_02_03_dce/binaries --instances 10 --verification-rounds 10 --allow aes_encrypt des_encrypt md5 rc4 sha1
cd -
```
Note that we build only 10 instances and use only 10 verification rounds (other than in our paper).

_Expected time (104 CPU cores): ~15 minutes_ 

## 2. Extract handler addresses

First, extract all handler and their addresses - to do so, switch to the [../../lokiattack](../../lokiattack) folder and run:
```
cd ../../lokiattack/
python3 extract_handler_addresses.py /home/user/evaluation/experiment_01_02_03_dce/binaries -o /home/user/evaluation/experiment_01_02_03_dce/dce_handler_addresses.txt --num-samples 1000
```
Note that we sample only 1000 handler to speedup evaluation (other than in our paper). Do not set `--num-samples` if you want to test all handlers.

_Expected time (104 CPU cores): ~1 second_ 

## 3. Run dead code eliminiation

Then, run the dead code elimination (again in the lokiattack directory):
```
python3 run.py compiler_optimizations /home/user/evaluation/experiment_01_02_03_dce/binaries static -o /home/user/evaluation/experiment_01_02_03_dce/dce_results.txt --handler-list /home/user/evaluation/experiment_01_02_03_dce/dce_handler_addresses.txt
cd -
```

_Expected time (104 CPU cores): ~30 seconds_ 

## 4. Evaluate results

Finally, evaluate the results using `eval_dead_code_elimination.py` and `eval_executed_handler.py` in this directory:

```
python3 eval_dead_code_elimination.py /home/user/evaluation/experiment_01_02_03_dce/dce_results.txt
python3 eval_executed_handler.py /home/user/evaluation/experiment_01_02_03_dce/binaries
```

_Expected time (104 CPU cores): ~1 second_ 

Compare the results against the ones reported in Table 1 (page 3), last column.
