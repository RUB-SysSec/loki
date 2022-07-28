#!/usr/bin/env bash

set -eu
set -o pipefail

PARALLEL_JOBS=${PARALLEL_JOBS:-1}

# install LLVM
# pushd /llvm > /dev/null
# sudo ninja install
# popd > /dev/null

# install z3
./install_z3.sh

# build C++ component
pushd translator > /dev/null
if [ ! -L llvm ]; then
    ln -s /llvm llvm
fi
if [ -d build ]; then
    rm -r build
fi
./build.sh
popd > /dev/null

# build Rust component
pushd obfuscator > /dev/null
cargo build -j "$PARALLEL_JOBS"
cargo build --release -j "$PARALLEL_JOBS"
popd > /dev/null

