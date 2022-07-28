#!/usr/bin/env bash

set -eu

PARALLEL_JOBS=${PARALLEL_JOBS:-1}

sudo apt install libboost1.62-all-dev

# install capstone (dependency of Triton)
if [ ! -d capstone ]; then
    git clone https://github.com/capstone-engine/capstone.git
    pushd capstone > /dev/null
    git checkout 4.0.2 # 3.0.5 # 4.0.2
    ./make.sh
    sudo ./make.sh install
    popd > /dev/null
fi;

# install Triton
git clone https://github.com/JonathanSalwan/Triton
cd Triton
git checkout v0.8.1
mkdir build ; cd build
# Z3_INCLUDE_DIRS=/home/user/.pyenv/versions/3.9.0/include Z3_LIBRARIES=$(readlink -f ../../loki/z3/build) cmake ..
cmake -DZ3_INTERFACE="" ..
make -j "$PARALLEL_JOBS"
sudo make install
ln -s /usr/lib/python3/dist-packages/triton.so /home/user/.pyenv/versions/3.9.0/lib/python3.9/site-packages/triton.so
