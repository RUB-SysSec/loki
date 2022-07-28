#!/usr/bin/env bash

set -o errexit # set -e
set -o nounset # set -u
set -o pipefail

PARALLEL_JOBS=${PARALLEL_JOBS:-1}

if [ -d build ]; then
	echo "Directory 'build' already exists!"
    pushd "build" > /dev/null
    make -j "$PARALLEL_JOBS"
    popd > /dev/null
else
    mkdir -p "build"
    pushd "build" > /dev/null
    cmake ..
    make -j "$PARALLEL_JOBS"
    popd > /dev/null
fi
