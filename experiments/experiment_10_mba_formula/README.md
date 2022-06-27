# Experiment 10 MBA Formula Deobfuscation

To test state-of-the-art MBA deobfuscation research (which works on MBA formulas rather than the binary level), we create MBA formulas. The MBA formulas are placed in different files (for each operation in (`+ - & | ^`)) and recursive rewriting depth (the format is `OPERATION_depthREWRITINGDETPH.txt`, e.g., `add_depth5.txt`).


## 1. Sample or build MBA formulas

Generating MBA formulas is a slow process (as we discard most of the MBAs produced by Loki to adhere to a simpler, more artifical format that can be processed by Loki's competitors); generating MBAs may take a couple of days. 

To speed up that process, we provide for your convenience an alternative: Sample a subset of MBAs from the ones we generated for our evaluation (provided in [./data](./data)). We will first describe this before describing how to generate MBA formulas from scratch.


### i) Sample MBA formulas
To sample 10 MBA formulas per operation (`+ - & | ^`) and recursive rewriting depth (i.e., how often Loki applied MBAs recursively), run:
```
mkdir -p /home/user/evaluation/experiment_10_mba_formulas/
python3 sample_mba_formulas.py 10 /home/user/evaluation/experiment_10_mba_formulas/mba_formulas
```
_Expected time (104 CPU cores): 1 second_

### ii) Generate new MBA formulas

Please notice that this process is very slow: We recommend using (a subset of) our pre-generated data instead (as described in the previous step).

To create these MBA formulas, we need to apply the [mba_formula_generation.patch](../../loki/obfuscator/mba_formula_generation.patch) patch.

Then use our wrapper script to generate MBAs

```
# apply patch
cd ../../loki/obfuscator
git apply mba_formula_generation.patch
# build patched binary
cargo build --release

# create binaries
cd -
mkdir -p /home/user/evaluation/experiment

python3 generate_mba_formulas.py --all -c 10 -o /home/user/evaluation/experiment_10_mba_formulas/mba_formulas

# undo patch
cd ../../loki/obfuscator
git checkout .
cd -
```

In [experiment.py](experiment.py), sampling is default behavior. To force the creation of new MBAs, use the `--generate-new-mbas` flag.


## 2. Run deobfuscation tools against these formulas

After creating MBA formulas, we can check how many of them can be simplified by the various tools. The tools will produce an output file for each MBA formula file (where the format for each line/MBA is): mba,simplified,groundtruth,CORRECT

### i) LokiAttack for MBA formulas
Run: 
```
mkdir -p /home/user/evaluation/experiment_10_mba_formulas/experiment_data/

cd deobfuscation_tools/lokiattack
python3 run_lokiattack.py -o /home/user/evaluation/experiment_10_mba_formulas/experiment_data /home/user/evaluation/experiment_10_mba_formulas/mba_formulas/*
cd -
```
_Expected time (104 CPU cores): 2 minutes_


### ii) MBA-Blast
Run:
```
cd deobfuscation_tools/mba_blast
python3 -m pip install --user numpy sympy
python3 run_mba_blast.py -o /home/user/evaluation/experiment_10_mba_formulas/experiment_data /home/user/evaluation/experiment_10_mba_formulas/mba_formulas/*
python3 -m pip uninstall -y numpy sympy
cd -
```
_Expected time (104 CPU cores): 15 minutes_

### iii) SSPAM
Run:
```
cd deobfuscation_tools/sspam
/home/user/.pyenv/versions/3.6.8/bin/python -m pip install --user sympy==0.7.4 astunparse~=1.3 z3-solver==4.8.7
/home/user/.pyenv/versions/3.6.8/bin/python run_sspam.py -o /home/user/evaluation/experiment_10_mba_formulas/experiment_data /home/user/evaluation/experiment_10_mba_formulas/mba_formulas/*
cd -
```
_Expected time (104 CPU cores): 1 hour 10 minutes_

Note that we use `/home/user/.pyenv/versions/3.6.8/bin/python`, as SSPAM does not work with newer Python versions.


### iv) NeuReduce

Unfortunately, the authors of the paper have unpublished NeuReduce and deleted their repository (https://github.com/nhpcc502/NeuReduce). Beyond that NeuReduce would require an old Tensorflow Docker container and special hardware in form of Nvidia GPUs to run the pre-trained models.


## 3. Draw conclusions
Each of the tools creates /home/user/evaluation/experiment_10_mba_formulas/experiment_data/$TOOL_stats.json files. For analysis, run:
```
python3 eval_mba_formula_results.py /home/user/evaluation/experiment_10_mba_formulas/experiment_data
```
_Expected time (104 CPU cores): 1 second_


Alternatively, you can create a plot with:
```
python3 -m pip install --user numpy scipy matplotlib
python3 plot_mba_formula.py /home/user/evaluaton/experiment_10_mba_formulas/experiment_data avg
```
_Expected time (104 CPU cores): 2 seconds_

This will print the graph from the paper. You can compare the data or graph to the plot in Figure 3, page 13, "Deobufscation of 1,000 artifical MBAs" in the paper. Given the different numbers of formulas evaluated (1,000 in paper vs 10 for faster reproduction), they may slightly differ but should clearly depict the same trend.
