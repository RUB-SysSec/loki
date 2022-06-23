# Experiments

Each directory represents one of the experiments from our paper. All numbered experiments match the experiments in the Evaluation of our paper. The [dead_code_elimination](./dead_code_elimination/) experiment allows to reproduce behavior of Table 1 (in the Introduction).

Each experiment has a README.md describing its individual steps. Furthemore, (where applicable) each directory has a convenience script reproducing the experiment.

To reduce time spent on reproducing our experiments, these scripts define (as global value in form of `NUM_INSTANCES` or `NUM_FORMULAS`) a lower number of targets to evaluate on than our actual evaluation (oftentimes 10 instead of 1,000). Feel free to change this value to your needs.
