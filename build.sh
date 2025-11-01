#!/bin/bash

OUTPUT_IMAGE=${1:-base_line_manip:irsl_one}
_TORCH_VER=${TORCH_VERSION:-2.9}

if [ ! -e irsl_docker_irsl_system ]; then
    git clone https://github.com/IRSL-tut/irsl_docker_irsl_system
fi

set -x

docker build . -f Dockerfile --build-arg TORCH_VER=${_TORCH_VER} -t ${OUTPUT_IMAGE}
