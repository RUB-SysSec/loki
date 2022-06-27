# Experiment 2 Coverage

As part of the revision requirements, we have checked coverage. This has 2 dimensions:
1) Make sure our inputs execute the full functionality of the original program. To do so, first verify the input program has indeed been correctly unrolled into a single basic block (for example, using the binja_script.py provided or your favorite disassembler). The outputs recorded in experiment 1 then indicate that full coverage on the original program has been achieved.
2) Use the tooling in `./tracer` to verify we achieve the same coverage on all VM handlers needed to represent the original code.

Note that we assume here you have conducted the [dead_code_elimination](../dead_code_elimination/) experiment before and built a number of binaries in `/home/user/evaluation/experiment_01_02_03_dce/`, which we will re-use here. If you have not, build binaries as follows:

## Build Binaries
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