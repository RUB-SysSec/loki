#!/bin/bash

USER_SUFFIX="$(id -u -n)"
NAME="loki-obfuscation"
IMAGE_NAME="${NAME}-${USER_SUFFIX}:latest"
CONTAINER_NAME="${NAME}-${USER_SUFFIX}"

