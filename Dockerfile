FROM repo.irsl.eiiris.tut.ac.jp/irsl_system:24.04_one

# ARG TORCH_VER=2.9
### 最新版適用のためにisriからダウンロード
### commit hash 9222eaf6dfddffdd7ba504c210d199866d1e963c でビルドを確認
# RUN (cd /; git clone https://github.com/IRSL-tut/RoboManipBaselines.git --recursive)
RUN (cd /; git clone https://github.com/isri-aist/RoboManipBaselines.git --recursive)

WORKDIR /RoboManipBaselines

RUN apt update -q -qq && \
    apt install -q -qq -y ffmpeg python3-venv libnppicc12 && \
    apt clean && \
    rm -rf /var/lib/apt/lists/

# RUN python3 -m venv /irsl_venv --copies --system-site-packages
RUN python3 -m venv /irsl_venv --copies

## RoboManipBaselines側で適当なバージョンを入れているのでそれを利用するために削除
## https://github.com/isri-aist/RoboManipBaselines/commit/dfa0f97c6359ca20b70769dbfca924a3f25c61c2
# ## install pytorch
# RUN <<EOF
# if [ -e /irsl_venv/bin/activate ]; then
#    source /irsl_venv/bin/activate
# fi
# mkdir -p /opt/python
# pip install --target /opt/python iceoryx2==0.7.0
# #
# if [ ${TORCH_VER} == '2.9' ]; then
#     pip install --break-system-packages torch==2.9.0 torchvision torchcodec==0.8
# elif [ ${TORCH_VER} == '2.8' ]; then
#     pip install --break-system-packages torch==2.8.0 torchvision==0.23.0 torchaudio==2.8.0 torchcodec==0.6 --index-url https://download.pytorch.org/whl/cu128
# elif [ ${TORCH_VER} == '2.7' ]; then
#     pip install --break-system-packages torch==2.7.1 torchvision==0.22.1 torchaudio==2.7.1 torchcodec==0.5 --index-url https://download.pytorch.org/whl/cu126
# else
#     set -e
#     [ 0 -eq 1 ] ## failed
# fi
# EOF

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

## Pi0
RUN source /irsl_venv/bin/activate && \
    cd /RoboManipBaselines && \
    pip install -e .[lerobot] && \
    cd third_party/lerobot && \
    pip install -e .[pi]

RUN source /irsl_venv/bin/activate && \
    (cd /; git clone https://github.com/huggingface/lerobot -b v0.4.4 --recursive) && \
    cd /lerobot && \
    pip install -e .[pi]

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

# task_descがないパターンがあったのでコードを修正して対応
RUN <<EOF
cd /RoboManipBaselines
cat << 'PATCH' | patch -p1
diff --git a/robo_manip_baselines/misc/ConvertRmbDataToLerobot.py b/robo_manip_baselines/misc/ConvertRmbDataToLerobot.py
index 8ae04f5..f60cc0f 100644
--- a/robo_manip_baselines/misc/ConvertRmbDataToLerobot.py
+++ b/robo_manip_baselines/misc/ConvertRmbDataToLerobot.py
@@ -189,6 +189,9 @@ class ConvertRmbDataToLerobot:
                 elif "task_desc" in rmb_data.attrs:
                     task_desc = rmb_data.attrs["task_desc"]
                 else:
+                    task_desc = None
+
+                if not task_desc:
                     env_name = rmb_data.attrs["env"]
                     if env_name == "MujocoUR5eCableEnv":
                         task_desc = "pass the cable between two poles"
PATCH
EOF
