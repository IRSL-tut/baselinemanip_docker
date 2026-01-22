
# How to start imitation learning


## Teleop (making a data set)

```
cd teleop
./baseline_bag.sh ## start storing data
#< controlling the robot to do the task
# Ctrl-C ## stop storing data
```

## Train

### Train (converting a bag to data-set)
```
cd train
./conv_bag_to_pkl.py <bag_dir> --outdir <pkl_dir>
```

```
./run.sh
cd project_research/train
./conv_pkl_to_rm.py <pkl_dir> --outdir <rmb_dir>
```

### Train

```
./run.sh

$ cd /RoboManipBaselines

$ python bin/Train.py Act \
--dataset_dir <rmb_dir> \
--checkpoint_dir <checkpoint_dir> \
--state_keys measured_joint_pos \
--action_keys command_joint_pos \
--camera_names hand \
--skip 2 \
--chunk_size 50 \
--num_epochs 20000 \
--save_interval 400

```

## Rollout

- Start to run the robot environment (Real or Simulation)

```
```
