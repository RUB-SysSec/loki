# Experiment 12 Limits of Program Synthesis

We create 10.000 random expressions of each depth and then use Syntia and try to synthesize them. Be advised that the time grows exponentially.

## 1. Create data

For each depth from 1 to the desired maximum, run in LokiAttack directory:
```
python3 synthesis_limits.py NUM_VARS DEPTH /home/user/evaluation/experiment_12_synthesis_limits/depth_DEPTH.json
```
NUM_VAR == DEPTH for uneven numbers; for even numbers, NUM_VARS == DEPTH - 1. This is as x + y has depth 3; x + (- y) has depth 4 (but only 3 variables).

## 2. Evaluate data
Evaluate the resulting files with `eval_synthesis_limits.py`:
```
python3 eval_synthesis_limits.py /home/user/evaluation/experiment_12_synthesis_limits
```

This will print some statistics for all available layers (and assert 10k expressions have been tested each).
