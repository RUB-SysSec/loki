#!/usr/bin/env bash

# This script will install
# * z3 (needed for Loki)
# * python packages needed by LokiAttack
# * Triton needed by byte-granular taint analysis
# * Intel Pin needed for experiment 2
# Intended for use within our Docker container

set -eu

if [ ! -f /.dockerenv ]; then
    echo "Did not find file '/.dockerenv' -- this script should be run inside our docker container"
    exit 1
fi;

echo "Installing Loki (including z3 dependency)"
pushd loki > /dev/null
./build.sh
popd > /dev/null

echo "Installing LokiAttack's Python dependencies"
pushd lokiattack > /dev/null
python3 -m pip install wheel
python3 -m pip install --user -r requirements.txt
echo "Installing Triton (used for byte-level taint analysis)"
if [ ! -d Triton ]; then
    rm -f /home/user/.pyenv/versions/3.9.0/lib/python3.9/site-packages/triton.so
    ./install_triton.sh
else
    echo "Triton directory already exists. Skipping.."
fi
popd > /dev/null

echo "Installing Pin for Experiment 2"
pushd experiments/experiment_02_coverage/tracer > /dev/null
./install_pin.sh
popd > /dev/null

echo "Done."
