#!/bin/bash

set -o errexit # set -e
set -o nounset # set -u
set -o pipefail

if [ -d build ]; then
	echo "Directory 'build' already exists!"
    pushd "build" > /dev/null
    make -j
    popd > /dev/null
else
    mkdir -p "build"
    pushd "build" > /dev/null
    cmake ..
    make -j
    popd > /dev/null
fi
