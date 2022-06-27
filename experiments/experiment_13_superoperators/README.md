# Experiment 13 Superoperators on the binary level

This experiment requires 4 steps. You can use our experiment_13.py script or alternatively execute them individually.

## 1. Build Binaries

First, we need to build binaries from which we can sample handlers. We use the following configuration, which applies no MBAs but superoperators.

```
# Settings:
    rewrite_mba: false,
    superoptimization: true,
    schedule_non_deterministic: true,
```

To build the binaries, run the following: 

```
# create binaries
cd ../../loki
mkdir -p /home/user/evaluation/experiment_13_superoperators_binary_level
python3 obfuscate.py /home/user/evaluation/experiment_13_superoperators_binary_level/binaries --instances 10 --allow aes_encrypt des_encrypt rc4 md5 sha1 --nomba --verification-rounds 0
cd -
```
_Expected time (104 CPU cores): 15 minutes_

Noteworthy, this will create only 10 obfuscated instances (instead of 400 as in the paper).

## 2. Extract handlers
We first need to extract handlers with their index and a valid key. We randomly sample 1,000 handler with one of their valid keys which we will then attempt to synthesize (in the paper, we used 10,000). To do so, run the `extract_handlers.py` script in LokiAttack.
```
cd ../../lokiattack
python3 extract_handlers.py /home/user/evaluation/experiment_13_superoperators_binary_level/binaries 1000 -o /home/user/evaluation/experiment_13_superoperators_binary_level/sampled_handlers.txt
```
_Expected time (104 CPU cores): 1 second_


## 3. Synthesize handlers
We then use Syntia to attempt to synthesize the handlers. We do so exclusively in the stronger dynamic setting. Additionally, we need to set the `--handler-list` flag to point to the file produced in the previous step.
```
# in lokiattack directory
python3 run.py synthesis /home/user/evaluation/experiment_13_superoperators_binary_level/binaries dynamic -o /home/user/evaluation/experiment_13_superoperators_binary_level/synthesis_results.txt --handler-list /home/user/evaluation/experiment_13_superoperators_binary_level/sampled_handlers.txt
cd -
```
_Expected time (104 CPU cores): 30 minutes_

## 4. Draw conclusions
Finally, we can analyze the outcome:
```
# dynamic attacker
python3 eval_synthesis.py /home/user/evaluation/experiment_13_superoperators_binary_level/synthesis_results.txt
```
_Expected time (104 CPU cores): 1 second_

This will print some statistics. You can compare the percentage of successful synthesis tasks to the one reported in the paper for Experiment 13.
