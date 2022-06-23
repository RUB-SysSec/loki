#!/bin/bash

set -eu

git clone https://github.com/Z3Prover/z3.git
cd z3
git checkout z3-4.8.7
python scripts/mk_make.py --python
cd build
make -j
sudo make install
sudo ln -s /home/user/loki/loki/z3/build/libz3.so /usr/lib/x86_64-linux-gnu/libz3.so

