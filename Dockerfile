### llvm_builder
FROM ubuntu:18.04 as llvm_builder

ARG TZ=Europe/Berlin
ARG DEBIAN_FRONTEND=noninteractive
RUN apt update && apt install -y \
    build-essential \
    git \
    make \
    cmake \
    curl \
    gcc \
    ninja-build \
    python3

ARG LLVM_DIR=/llvm_src
ARG LLVM_INSTALL_DIR=/llvm

# create LLVM 
# increase git pull timeout 
RUN git config --global http.postBuffer 1048576000

WORKDIR $LLVM_DIR
RUN git clone https://github.com/llvm/llvm-project.git
WORKDIR llvm-project
RUN git checkout e6f22596e5de7f4fc6f1de4725d4aa9b6aeef4aa

# will be overriden by docker_build.sh script
ARG PARALLEL_JOBS=2

# build type used to be RelWithDebInfo (but is 40GB instead of 1.5)
WORKDIR $LLVM_INSTALL_DIR
RUN cmake \
  -G "Ninja" \
  -DCMAKE_EXPORT_COMPILE_COMMANDS=ON \
  -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_INSTALL_PREFIX=$LLVM_INSTALL_DIR \
  -DLLVM_CCACHE_DIR=$LLVM_DIR/llvm-project/llvm/ccache \
  -DLLVM_ENABLE_CXX1Y=On \
  -DLLVM_ENABLE_IDE=On \
  -DLLVM_ENABLE_PROJECTS=clang \
  -DLLVM_TARGETS_TO_BUILD="X86" \
  -DLLVM_PARALLEL_COMPILE_JOBS=$PARALLEL_JOBS \
  -DLLVM_PARALLEL_LINK_JOBS=$PARALLEL_JOBS \
  -DLLVM_USE_LINKER=gold \
  -DLLVM_BUILD_LLVM_DYLIB=On \
  $LLVM_DIR/llvm-project/llvm \
  && ninja -j ${PARALLEL_JOBS}
# end llvm_builder

FROM ubuntu:18.04
COPY --from=llvm_builder /llvm/ /llvm/
COPY --from=llvm_builder /llvm_src /llvm_src


FROM ubuntu:18.04

# import LLVM
COPY --from=llvm_builder /llvm /llvm
COPY --from=llvm_builder /llvm_src /llvm_src


ARG DEBIAN_FRONTEND=noninteractive
ARG TZ=Europe/Berlin

RUN apt update && apt install -y \
    build-essential git \
        curl wget \
        make cmake ninja-build \
        locales locales-all \
        sudo \
        neovim tree \
        bear ccache \
        gdb strace ltrace \
        htop \
        parallel psmisc \
        zip unzip \
        screen tmux \
        linux-tools-common linux-tools-generic \
        zsh powerline fonts-powerline \
        libssl-dev zlib1g-dev \
        libbz2-dev libreadline-dev libsqlite3-dev \
        libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev \
        libboost1.62-all-dev \
        automake

# MISC NOTES
# * psmisc contains killall

RUN locale-gen en_US.UTF-8
ARG USER_UID=1000
ARG USER_GID=1000

RUN echo "%sudo ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers
RUN echo "user ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers

WORKDIR /tmp
RUN update-locale LANG=en_US.UTF-8
ENV LANG=en_US.UTF-8

RUN groupadd -g ${USER_GID} user

# add user (-l flag to prevent faillog / lastlog from becoming huge)
RUN useradd -l --shell /bin/bash -c "" -m -u ${USER_UID} -g user -G sudo user

WORKDIR "/home/user"
USER user

# install rust
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | bash -s -- -q -y --default-toolchain nightly
ENV PATH="/home/user/.cargo/bin:${PATH}"

# install PYENV
RUN curl https://pyenv.run | bash
RUN /home/user/.pyenv/bin/pyenv install 3.6.8
RUN /home/user/.pyenv/bin/pyenv install 3.9.0
RUN /home/user/.pyenv/bin/pyenv global 3.9.0

# zsh agnoster
RUN sh -c "$(wget -O- https://raw.githubusercontent.com/deluan/zsh-in-docker/master/zsh-in-docker.sh)" --     -t agnoster
