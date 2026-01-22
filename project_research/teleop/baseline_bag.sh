#!/bin/bash

rosbag record -b 16384 --chunksize 1024 \
/divided_robot/gripper_controller/state \
/divided_robot/trajectory_controller/state \
/divided_robot/joint_states \
/Camera0/color/image_raw
