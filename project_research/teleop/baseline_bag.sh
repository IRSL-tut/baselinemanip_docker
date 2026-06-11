#!/bin/bash
rosbag record -b 16384 --chunksize 1024 \
/AssembleRobot/gripper_controller/state \
/AssembleRobot/trajectory_controller/state \
/AssembleRobot/joint_states \
/AssembleRobot/Camera0/color/image_raw
