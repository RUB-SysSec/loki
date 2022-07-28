#!/usr/bin/env bash

set -e

source docker_data/docker_config.sh

# change this if you want to compile on fewer cores
PARALLEL_JOBS=$(nproc)
echo "Using $PARALLEL_JOBS CPU cores -- we recommend running this only on servers with >= 32 cores and at least 64GB RAM"

docker build --build-arg USER_UID="$(id -u)" --build-arg USER_GID="$(id -g)" --build-arg PARALLEL_JOBS="$PARALLEL_JOBS" $@ -t $IMAGE_NAME .
