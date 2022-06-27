# Tracer

Run inputs (generated for experiment_01_correctness) and ensure we achieve full coverage. There are two scripts for your convenience:

* `mgr.py` will run all provided inputs and trace them using Intel Pin. This is *slow*.
* `subset_mgr.py` will run only a number of instances or subset of inputs, which is more convenient for testing the tracer.

There is a third script, `patch.py`, which is needed for performance reasons.

## Prerequisites

Running the tracer assumes that you have run the input-generator of Experiment 1 before. This is needed to have the inputs for tracing.


## Setup

Install Intel Pin using `./install_pin.sh` -- note that the PIN_ROOT in `makefile` must be correct. The script will attempt to set it automatically, but you might want to check if stuff is not working as expected. Then run `make` to build our pintool.

Finally, make sure you have used the tooling needed to patch the binaries (such that the loop in main is executed only once) -- to do so, in scripts git directory, run:
```
./install_pin.sh
make
python3 patch.py /home/user/evaluation/experiment_01_02_03_dce/binaries
```

_Expected time (104 CPU cores): 1 second_ 

## Run
Run tracing:
```
# trace only 10k inputs per instance -- expected runtime: 2 minutes
python3 subset_mgr.py --only aes_encrypt des_encrypt md5 rc4 sha1 -i ../../experiment_01_correctness/inputs.json /home/user/evaluation/experiment_01_02_03_dce/binaries --input-subset-size 10000

# Exemplary run commands to trace *all* (very slow!)
# python3 mgr.py --only aes_encrypt des_encrypt md5 rc4 sha1 -i ../../experiment_01_correctness/inputs.json /home/user/evaluation/experiment_01_02_03_dce/binaries
```
This will create a `pin_vm_trace.json` and `pin_vm_stats.txt` in each traced instance directory. In the end, the `mgr.py` or `subset_mgr.py` will print the number of failing instances (should be 0 for all targets).

_Expected time (104 CPU cores): 2 minutes_ 
