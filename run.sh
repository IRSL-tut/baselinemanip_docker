#!/bin/bash

irsl_docker_irsl_system/run.sh -w $(pwd) --docker-option --shm-size=1g --name robomanip --image base_line_manip:irsl_one

### for exec
# docker exec -it roboamnip bash
