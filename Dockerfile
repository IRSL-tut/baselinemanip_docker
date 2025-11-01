FROM repo.irsl.eiiris.tut.ac.jp/irsl_system:one

###
RUN (cd /; git clone https://github.com/isri-aist/RoboManipBaselines.git --recursive)

WORKDIR /RoboManipBaselines

RUN apt update -q -qq && \
    apt install -q -qq -y ffmpeg python3-venv && \
    apt clean && \
    rm -rf /var/lib/apt/lists/

RUN python3 -m venv /irsl_venv --copies

## install pytorch
RUN source /irsl_venv/bin/activate && \
    pip install --break-system-packages torch==2.9.0 torchvision
## torch 2.8.0 / cuda 12.8 | failed?
#    pip install --break-system-packages torch==2.8.0 torchvision==0.23.0 torchaudio==2.8.0 --index-url https://download.pytorch.org/whl/cu128
## torch 2.7.1 / cuda12.6
#    pip install --break-system-packages torch==2.7.1 torchvision==0.22.1 torchaudio==2.7.1 --index-url https://download.pytorch.org/whl/cu126
## torch 2.9 / cuda12.8 | success
#    pip install --break-system-packages torch==2.9.0 torchvision

RUN source /irsl_venv/bin/activate && \
    cd /RoboManipBaselines && \
    pip install -e .[act]  && \
    cd third_party/act/detr && \
    pip install -e .

## add for fix torch version
#    sed -i -e 's@"torch"@"torch<2.9"@' pyproject.toml && \

## SARNN
RUN source /irsl_venv/bin/activate && \
    cd /RoboManipBaselines && \
    pip install -e .[sarnn] && \ 
    cd third_party/eipl && \
    pip install -e .

## Diffusion Policy
RUN apt update -q -qq && \
    apt install -q -qq -y libosmesa6-dev libglfw3 patchelf && \
    apt clean && \
    rm -rf /var/lib/apt/lists/
# libgl1-mesa-glx is not required in irsl_system
RUN source /irsl_venv/bin/activate && \
    cd /RoboManipBaselines && \
    pip install -e .[diffusion-policy] && \
    cd third_party/diffusion_policy && \
    pip install -e .

### patched by IRSL
RUN <<EOF
cd /RoboManipBaselines
cat - << _DOC_ | patch -p1
diff --git a/robo_manip_baselines/common/base/TrainBase.py b/robo_manip_baselines/common/base/TrainBase.py
index 5ef7ab7..4918b3d 100644
--- a/robo_manip_baselines/common/base/TrainBase.py
+++ b/robo_manip_baselines/common/base/TrainBase.py
@@ -168,7 +168,7 @@ class TrainBase(ABC):
         )
 
         parser.add_argument("--seed", type=int, default=42, help="random seed")
-
+        parser.add_argument("--save_interval", type=int, default=100, help="IRSL save_interval")
         self.set_additional_args(parser)
 
         if argv is None:
diff --git a/robo_manip_baselines/policy/act/TrainAct.py b/robo_manip_baselines/policy/act/TrainAct.py
index 78655d4..6140c10 100644
--- a/robo_manip_baselines/policy/act/TrainAct.py
+++ b/robo_manip_baselines/policy/act/TrainAct.py
@@ -97,8 +97,8 @@ class TrainAct(TrainBase):
                 self.update_best_ckpt(epoch_summary)
 
             # Save current checkpoint
-            if epoch % max(self.args.num_epochs // 10, 1) == 0:
-                self.save_current_ckpt(f"epoch{epoch:0>3}")
+            if epoch % min(self.args.save_interval, max(self.args.num_epochs // 10, 1)) == 0:
+                self.save_current_ckpt(f"epoch{epoch:0>5}")
 
         # Save last checkpoint
         self.save_current_ckpt("last")
diff --git a/robo_manip_baselines/policy/diffusion_policy/TrainDiffusionPolicy.py b/robo_manip_baselines/policy/diffusion_policy/TrainDiffusionPolicy.py
index 938e8db..5d3bac2 100644
--- a/robo_manip_baselines/policy/diffusion_policy/TrainDiffusionPolicy.py
+++ b/robo_manip_baselines/policy/diffusion_policy/TrainDiffusionPolicy.py
@@ -336,8 +336,8 @@ class TrainDiffusionPolicy(TrainBase):
             policy.train()
 
             # Save current checkpoint
-            if epoch % max(self.args.num_epochs // 10, 1) == 0:
-                self.save_current_ckpt(f"epoch{epoch:0>4}", policy=policy)
+            if epoch % min(self.args.save_interval, max(self.args.num_epochs // 10, 1)) == 0:
+                self.save_current_ckpt(f"epoch{epoch:0>5}", policy=policy)
 
         # Save last checkpoint
         self.save_current_ckpt("last", policy=policy)
diff --git a/robo_manip_baselines/policy/sarnn/TrainSarnn.py b/robo_manip_baselines/policy/sarnn/TrainSarnn.py
index 6f15a45..fc5c9fc 100644
--- a/robo_manip_baselines/policy/sarnn/TrainSarnn.py
+++ b/robo_manip_baselines/policy/sarnn/TrainSarnn.py
@@ -243,8 +243,8 @@ class TrainSarnn(TrainBase):
                 self.update_best_ckpt(epoch_summary)
 
             # Save current checkpoint
-            if epoch % max(self.args.num_epochs // 10, 1) == 0:
-                self.save_current_ckpt(f"epoch{epoch:0>4}")
+            if epoch % min(self.args.save_interval, max(self.args.num_epochs // 10, 1)) == 0:
+                self.save_current_ckpt(f"epoch{epoch:0>5}")
 
         # Save last checkpoint
         self.save_current_ckpt("last")
_DOC_
EOF
