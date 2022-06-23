# Loki: Hardening Code Obfuscation Against Automated Attacks

Loki is an academic obfuscator prototype developed to showcase new VM handler hardening techniques.

# Installation

The easiest way to use Loki is Docker.
## Docker
We provide a Dockerfile and a few convenience/helper scripts.

### Build docker image
Run `./docker_build.sh` -- the image name is set in [docker_data/docker_config.sh](docker_data/docker_config.sh).

### Run docker container
Run `./docker_run.sh` twice: First time, the docker container is started. If running `./docker_run.sh` while the container is running, you are connected (`/bin/zsh`). The bash and zsh history are saved (as is zshrc) in [docker_data/](./docker_data/). This directory is available as volume within the container as `/home/user/loki`, which allows to copy files to/from the container.

### Stop docker container
To stop (and delete) the container, run `./docker_stop.sh`.


# Structure
This repository is structured as follows:

1) [loki](./loki): contains our prototype of an obfuscator, testcases, and a script to generate obfuscated targets
2) [lokiattack](./lokiattack): contains our evaluation tooling to attack binaries obfuscated by Loki
3) [experiments](./experiments): all experiments of our evaluation, documented and with scripts to reproduce them



# Contact

For more information, contact [m_u00d8](https://github.com/mu00d8) ([@m_u00d8](https://twitter.com/m_u00d8)) or [mrphrazer](https://github.com/mrphrazer) ([@mr_phrazer](https://twitter.com/mr_phrazer)).

