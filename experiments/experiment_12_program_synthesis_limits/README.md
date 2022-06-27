# Experiment 12 Limits of Program Synthesis

We create 10.000 random expressions of each depth and then use Syntia and try to synthesize them. Be advised that the runtime grows quickly.

To follow through with this experiment, run experiment_12.py:
```
python3 experiment_12.py --num-expressions 100
```
_Expected time (104 CPU cores): 40 minutes_ 

We recommend using 100 expressions instead of 10000 (as in the paper) to keep a reasonable runtime.

Alternatively, instead of running `experiment_12.py`, you can follow these steps:

## 1. Create data

For each depth from 1 to the desired maximum (paper: 20), run in the LokiAttack directory:
```
python3 synthesis_limits.py NUM_VARS DEPTH NUM_EXPRESSIONS /home/user/evaluation/experiment_12_synthesis_limits/depth_DEPTH.json
```
`NUM_VAR` == `DEPTH` for uneven numbers; for even numbers, `NUM_VARS` == `DEPTH` - 1. This is as x + y has depth 3; x + (- y) has depth 4 (but only 3 variables). `NUM_EXPRESSIONS` refers to the number of expressions tested per depth.

## 2. Evaluate data
Evaluate the resulting files with `eval_synthesis_limits.py`:
```
python3 eval_synthesis_limits.py /home/user/evaluation/experiment_12_synthesis_limits
```
_Expected time (104 CPU cores): 1 second_ 

This will print some statistics for all available layers. You can compare these numbers to the ones visible in Figure 5, page 15, "Probability of Synthesizing Formulas of Depth N" in the paper.

Alternatively, you can plot the results:
```
python3 -m pip install --user matplotlib scipy
python3 plot_synthesis_limits.py /home/user/evaluation/experiment_12_synthesis_limits/ 100
```
Due to the lower number of expressions tested (100 instead of 10,000), the plot may appear differently (e.g., confidence intervals), however, the trend should be clearly visible. 
