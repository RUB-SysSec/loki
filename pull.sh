#!/usr/bin/env bash

set -eu

# This script pulls docker image from Dockerhub and changes the tag 
# such that the convenience scripts docker_X.sh still work as expected

# pull image
echo "Pulling mu00d8/loki-obfuscation"
docker pull mu00d8/loki-obfuscation

# re-tag image
echo "Changing tag to loki-obfuscation:latest"
docker tag mu00d8/loki-obfuscation:latest loki-obfuscation:latest
