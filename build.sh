#!/bin/bash

if [ ! -e irsl_docker_irsl_system ]; then
    git clone https://github.com/IRSL-tut/irsl_docker_irsl_system
fi

docker build . -f Dockerfile -t base_line_manip:irsl_one
