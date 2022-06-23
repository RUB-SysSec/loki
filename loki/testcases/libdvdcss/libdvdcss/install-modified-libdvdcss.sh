#!/bin/bash

autoreconf -i

export LLVM_INSTALLED=$(pwd)/../../../instruction_handler_implementation/llvm 
export INSTALL_DIR=$(pwd)/libdvdcss-build
export INSTALL_DIR_MOD=$(pwd)/libdvdcss-build-modified

export CC=$LLVM_INSTALLED/bin/clang
export CXX=$LLVM_INSTALLED/bin/clang++

# reverse patch (might have already been applied)
patch -R -N ./src/css.c patch_DecryptKey.diff
echo "[+] Configuring plain libdvdcss"
./configure --prefix=$INSTALL_DIR
make -j
make install
echo "[+] Installed libdvdcss to $INSTALL_DIR"

# Apply patch and rebuild:
echo "[+] Configuring obfuscated libdvdcss"
patch -N ./src/css.c patch_DecryptKey.diff
./configure --prefix=$INSTALL_DIR_MOD
make -j 
make install
echo "[+] Installed obfuscated libdvdcss to $INSTALL_DIR_MOD"

