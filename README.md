# baselinemanip_docker

Files for using RoboManipBaselines

https://github.com/isri-aist/RoboManipBaselines/tree/master

## Start

``` bash
./run.sh
```

## Sample

``` bash
cd /RoboManip
source venv/bin/activate
```

``` bash
cd RoboManipBaselines/robo_manip_baselines
python ./bin/Rollout.py Act MujocoUR5eCable --checkpoint /userdir/policy_best.ckpt --world_idx 0
```

policy_best.ckpt shoud be downloaded.

https://github.com/isri-aist/RoboManipBaselines/tree/master

## Build
``` bash
./build.sh
```
