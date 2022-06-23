# Tracer

Run inputs (generated for experiment_01_correctness) and ensure we achieve full coverage. There are two scripts for your convenience:

* `mgr.py` will run all provided inputs and trace them using Intel Pin. This is *slow*.
* `subset_mgr.py` will run only a number of instances (set to 10), which is more convenient for testing the tracer out.

There is a third script, `patch.py`, which is needed for performance reasons.


## Setup

Install Intel Pin using `./install_pin.sh` -- note that the PIN_ROOT in `makefile` must be correct. The script will attempt to set it automatically, but you might want to check if stuff is not working as expected.

Then run `make` to build our pintool.

Finally, make sure you have used the tooling needed to patch the binaries (such that the loop in main is executed only once) -- to do so, in scripts git directory, run:
```
python3 patch.py ~/evaluation/eval_crypto_nomba_0108/workdirs/
[...]
```

## Run
Exemplary run commands:
```
python3 mgr.py --only aes_encrypt -i ../inputs.json ~/evaluation/eval_crypto_nomba_0108
```

## Artifact Evaluation
In summary, run the following commands to build and run our tooling:
```
./install_pin.sh
make

python3 patch.py /home/user/evaluation/experiment_01_02_03_dce/

# testing only 10 random instances (use mgr.py instead of subset_mgr.py to test all)
python3 subset_mgr.py --only aes_encrypt des_encrypt md5 rc4 sha1 -i ../../experiment_01_correctness/inputs.json /home/user/evaluation/experiment_01_02_03_dce/
```
