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
mkdir -p /home/user/evaluation/experiment_13_superoperators_binary_level
./obfuscate.py /home/user/evaluation/experiment_13_superoperators_binary_level/binaries --instances 400 --allow aes_encrypt des_encrypt rc4 md5 sha1 --nomba --verification-rounds 1000
```

## 2. Extract handlers
We first need to extract handlers with their index and a valid key. We randomly sample 10000 handler with one of their valid keys which we will then attempt to synthesize. To do so, run the `extract_handlers.py` script in LokiAttack.
```
python3 extract_handlers.py /home/user/evaluation/experiment_13_superoperators_binary_level/binaries 10000 -o /home/user/evaluation/experiment_13_superoperators_binary_level/sampled_handlers.txt
```

## 3. Synthesize handlers
We then use Syntia to attempt to synthesize the handlers. We do so exclusively in the stronger dynamic setting. Additionally, we need t oset the `--handler-list` flag to point to the file produced in the previous step.
```
# dynamic attacker
python3 run.py synthesis /home/user/evaluation/experiment_13_superoperators_binary_level/binaries dynamic -o /home/user/evaluation/experiment_13_superoperators_binary_level/synthesis_results.txt --handler-list /home/user/evaluation/experiment_13_superoperators_binary_level/sampled_handlers.txt
```

## 4. Draw conclusions
Finally, we can analyze the outcome:
```
# dynamic attacker
python3 eval_synthesis.py /home/user/evaluation/experiment_13_superoperators_binary_level/synthesis_results.txt
```
This will print some statistics.
