#!/bin/bash

source /irsl_venv/bin/activate
# python -u interfaces_on_rolloutAct.py --checkpoint /userdir/chk001_a/policy_last.ckpt
python -u interfaces_on_rolloutAct.py --checkpoint /userdir/robot_checkpoint/policy_last.ckpt
