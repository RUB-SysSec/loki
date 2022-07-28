#!/usr/bin/env bash

set -eu

PARALLEL_JOBS=${PARALLEL_JOBS:-1}

if [ ! -d z3 ]; then
    git clone https://github.com/Z3Prover/z3.git
else
    echo "Directory z3 already exists. Not cloning.."
fi

cd z3
git checkout z3-4.8.7

# install with python to pyenv dir
python3 scripts/mk_make.py --python
cd build
make -j "$PARALLEL_JOBS"
sudo make install

# install without python to /usr/local
cd ..
rm -r build
python3 scripts/mk_make.py --prefix=/usr
cd build
make -j "$PARALLEL_JOBS"
sudo make install
