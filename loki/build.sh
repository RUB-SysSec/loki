#!/bin/bash

set -eu
set -o pipefail

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
./build.sh
popd > /dev/null

# build Rust component
pushd transformer > /dev/null
cargo build
cargo build --release
popd > /dev/null

