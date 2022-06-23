# Experiment 3 Overhead

We measure overhead both in terms of runtime (runtime_overhead.py) and size (size_overhead.py).

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
mkdir -p /home/user/evaluation/experiment_01_02_03_dce/
./obfuscate.py /home/user/evaluation/experiment_01_02_03_dce/binaries --instances 10 --allow aes_encrypt des_encrypt md5 rc4 sha1
```

## 2. Measure runtime overhead

To measure the runtime overhead, run the following command:
```
python3 runtime_overhead.py /home/user/evaluation/experiment_01_02_03_dce/binaries
```
Note that this must actually run each binary multiple times; each input tested is internally run 10 thousand times and the average time reported. This may take some time. Runtime overhead can be found in the log file.

## 3. Measure size overhead

To measure the size overhead, run the following command:
```
python3 size_overhead.py /home/user/evaluation/experiment_01_02_03_dce/binaries
```
As this measues overhead in terms of disk usage, this is fast. Size overhead can be found in the log file.
