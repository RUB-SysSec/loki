# Experiment 3 Overhead

We measure overhead both in terms of runtime (runtime_overhead.py) and size (size_overhead.py). You can compare the results to the numbers reported in Table 2, page 11, of our paper.

To conduct this experiment, either run experiment_03.py or walk through the following steps:

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

## 2. Measure runtime overhead

To measure the runtime overhead, run the following command:
```
python3 runtime_overhead.py /home/user/evaluation/experiment_01_02_03_dce/binaries
```
Note that this must actually run each binary multiple times; each input tested is internally run 10 thousand times and the average time reported. Runtime overhead can be found in the log file.

_Expected time (104 CPU cores): 2 minutes_ 

## 3. Measure size overhead

To measure the size overhead, run the following command:
```
python3 size_overhead.py /home/user/evaluation/experiment_01_02_03_dce/binaries
```
As this measues overhead in terms of disk usage, this is fast. Size overhead can be found in the log file.

_Expected time (104 CPU cores): 1 second_
