# LokiAttack

LokiAttack describes our framework to attack Loki's handler. It has a base framework ([lokiattack](./lokiattack)) that identifies all of Loki's handler in a binary and extracts all paths. You then can mount a specific attack technique using a plugin (cf. plugin_*.py files).

## Installation
Install the Python dependencies in [requirements.txt](./requirements.txt):
```
python3 -m pip install --user -r requirements.txt
```

## Usage
We provide a wrapper script in form of [run.py](./run.py).
```
python3 run.py PLUGIN_NAME PATH_TO_EVAL_DIR ATTACKER_TYPE

# view all options
python3 run.py --help

# one example (checkout our experiments for more):
python3 run.py se /home/user/evaluation/experiment_06_07_08_syntactic_simplification/binaries static
```
