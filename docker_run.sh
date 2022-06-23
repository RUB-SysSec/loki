#!/bin/bash

set -eu
set -o pipefail

source docker_data/docker_config.sh
export DISPLAY=:0.0

function yes_no() {
    if [[ "$1" == "yes" || "$1" == "y" ]]; then
        return 0
    else
        return 1
    fi
}

container="$(docker ps --filter="name=$CONTAINER_NAME" --latest --quiet)"
if [[ -n "$container" ]]; then
    # Connec to already running container
    echo "[+] Found running instance: $container, connecting..."
    cmd="docker start $container"
    echo "$cmd"
    $cmd
    if [[ -v NO_TTY ]]; then
        HAS_TTY=""
    else
        HAS_TTY="-t"
    fi
    cmd="docker exec -i $HAS_TTY --workdir /home/user/loki --user "$UID:$(id -g)" $container zsh"
    echo "$cmd"
    $cmd
    exit 0
fi

touch "$PWD/docker_data/bash_history"
touch "$PWD/docker_data/zsh_history"

echo "[+] Creating new container..."
cmd="docker run -t -d --privileged -v $PWD:/home/user/loki \
    -v $PWD/docker_data/zshrc:/home/user/.zshrc \
    -v $PWD/docker_data/zsh_history:/home/user/.zsh_history \
    -v $PWD/docker_data/bash_history:/home/user/.bash_history \
    -v $PWD/docker_data/init.vim:/home/user/.config/nvim/init.vim \
    -v $PWD/docker_data/vscode-data:/home/user/.config/Code
    --net=host \
    --mount type=tmpfs,destination=/tmp,tmpfs-mode=777 \
    --ulimit msgqueue=2097152000 \
    --shm-size=16G \
    --name $CONTAINER_NAME"

if [[ -f "/home/$USER/.gitconfig" ]]; then
    cmd+=" -v /home/$USER/.gitconfig:/home/user/.gitconfig"
fi

cmd+=" ${IMAGE_NAME} /bin/cat"

echo "$cmd"
$cmd

echo "[+] Rerun run.sh to connect to the new container."

