#!/bin/bash

set -e

source docker_data/docker_config.sh

docker build --build-arg USER_UID="$(id -u)" --build-arg USER_GID="$(id -g)" $@ -t $IMAGE_NAME .

