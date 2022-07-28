#!/usr/bin/env bash

set -eu

PARALLEL_JOBS=${PARALLEL_JOBS:-1}

PIN_DIR=pin-3.23-98579-gb15ab7903-gcc-linux
PIN_FILE="$PIN_DIR.tar.gz"

if [ ! -f "$PIN_FILE" ]; then
	wget "https://software.intel.com/sites/landingpage/pintool/downloads/$PIN_FILE"
fi

if [ ! -d "$PIN_DIR" ]; then
	tar -xzf "$PIN_FILE"
fi

if [ ! -d "./pin" ]; then
	ln -s $PIN_DIR pin
fi

# fix PIN_ROOT in makefile
sed -i "s?PIN_ROOT=/opt/pin?PIN_ROOT=$(pwd)/pin?g" makefile

make -j "$PARALLEL_JOBS"
