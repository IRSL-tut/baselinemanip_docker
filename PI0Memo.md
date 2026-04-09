# PI0 memo

## useful info.
- https://github.com/isri-aist/RoboManipBaselines/tree/master/robo_manip_baselines/policy/pi0
    - ここにあることをトレース．

## Dockerfileの変更 (commit hash: 8d95b487c32cb7e21da832dabdb559d4714cccf7との比較)
- RoboManipBaselinesを本家のを利用するように変更
- ~~↑に合わせてパッチは当てないように変更．（単純に対応するのがめんどくさいだけなので後で考える）~~
    - 取り込めそうなのでそのまま取り込み
- lerobotのインストールを実施するように変更．
- dataset convertのスクリプト`ConvertRmbDataToLerobot.py`をpatchで修正．
    - task descriptionが正しくセットされない場合があったので対応．
        - これ作者の意図としては`--task_desc`オプションで書いてほしいというだろうけど，複数のデータを混ぜて学習することを考えるともうちょっと何かできるとうれしい．
    - ~~データセット内の統計データを取得する処理を変更~~
        - ~~当該部分が遅すぎる．（データのコンバートに2時間なのに統計データ4時間越えとかになる）~~
        - ~~原因はdataset[i]でのアクセスが遅いがこれを必要key分だけアクセスしていることなので，dataset[i]には1回だけアクセスして各key用のデータを取得し保持するように変更．メモリ使用量が気になるところだが，MujocoUR5ePickで実行する分にはそんなに気にはならない．~~
    - ~~`stats.json`の形式に一部不備があるため修正~~
    - ↑は本家に[PR](https://github.com/isri-aist/RoboManipBaselines/pull/42)出して通ったので削除

## run.shの変更 (commit hash: 8d95b487c32cb7e21da832dabdb559d4714cccf7との比較)
- dataloader用のshmが必要だったので8Gに増やした

## Image build
```bash
./build.sh
```

## try script

```bash 
# データセットの用意
mkdir -p dataset/rmb/MujocoUR5ePick
cd dataset/rmb/MujocoUR5ePick
## https://github.com/isri-aist/RoboManipBaselines/blob/master/doc/dataset_list.md
## これのなかにあるMujocoUR5ePickを利用
wget https://www.dropbox.com/scl/fo/az0cpxc8ar7p3i022door/ADB3r9mvSycMhGLiTXroSd4?rlkey=nxgkawcsm8ti7zcg8tf9npnot
unzip ADB3r9mvSycMhGLiTXroSd4?rlkey=nxgkawcsm8ti7zcg8tf9npnot
rm ADB3r9mvSycMhGLiTXroSd4?rlkey=nxgkawcsm8ti7zcg8tf9npnot


# データセット変換
# 変換元のデータセットは適当なディレクトリを指定すると再帰探索するので，中に複数種類入れるとよさそう．
python /RoboManipBaselines/robo_manip_baselines/misc/ConvertRmbDataToLerobot.py dataset/rmb/MujocoUR5ePick --output_dir dataset/lerobot

# Hugging Face login
## アカウント作成->gemmaのacknowledge licence-> tokenの取得が必要
## tokenはhf auth loginのコマンドを打つと取得のためのURLが出てくる
hf auth login

# 学習
# readmeのコマンド例と違うのは2点
# - batch_sizeを削減(32->4)．GPUに乗せるために小さくしている．
# - freeze_vision_encoder=true としvision encoderはトレーニングしないようにしている（トレーニングの高速化に寄与）
lerobot-train --dataset.root=dataset/lerobot --output_dir trained --dataset.repo_id=null --policy.type=pi0 --job_name=pi0_training --policy.pretrained_path=lerobot/pi0_base   --policy.repo_id=local_repo   --policy.compile_model=true  --policy.gradient_checkpointing=false --policy.dtype=bfloat16 --policy.freeze_vision_encoder=true --policy.train_expert_only=true --policy.push_to_hub=false --policy.input_features='{"observation.images.front_rgb": {"shape":[3,224,224], "type":"VISUAL"}, "observation.images.hand_rgb": {"shape":[3,224,224], "type":"VISUAL"}, "observation.state": {"shape":[7], "type":"STATE"}}'  --policy.n_action_steps=8 --policy.chunk_size=16 --batch_size=4

# 推論 (推論だけ行う場合でもHungging Faceのログインは必要)
python3 /RoboManipBaselines/robo_manip_baselines/bin/Rollout.py Pi0 MujocoUR5ePick --checkpoint trained/checkpoints/last/pretrained_model --world_idx 0 --task_desc "Pick up the spam can and place it in the black basket."

```
## MujocoUR5ePickのタスクについて
```
# python3 -c 'import pandas as pd; df = pd.read_parquet("dataset/lerobot/meta/tasks.parquet"); print(df.to_string())' 
                                                                                                  task_index
Pick up the large red box and place it in the black basket.                                                0
Pick up the large red box and place it in the white basket.                                                1
Pick up the spam can and place it in the black basket.                                                     2
Pick up the spam can and place it in the white basket.                                                     3
Pick up the light green dish and place it in the black basket.                                             4
Pick up the light green dish and place it in the white basket.                                             5
Pick up the small brown box and place it in the black basket.                                              6
Pick up the small brown box and place it in the white basket.                                              7
Pick up the red cup and place it in the black basket.                                                      8
Pick up the red cup and place it in the white basket.                                                      9
Pick up the plastic bottle with a black body and an orange cap and place it in the black basket.          10
Pick up the plastic bottle with a black body and an orange cap and place it in the white basket.          11
Pick up the chinese spoon and place it in the black basket.                                               12
Pick up the chinese spoon and place it in the white basket.                                               13
Pick up the plastic bottle with a blue body and a white cap and place it in the black basket.             14
Pick up the plastic bottle with a blue body and a white cap and place it in the white basket.             15
Pick up the purple tape and place it in the black basket.                                                 16
Pick up the purple tape and place it in the white basket.                                                 17
```

<!--
parquetファイルの見方
python3 -c 'import pandas as pd; df = pd.read_parquet("dataset/lerobot/meta/tasks.parquet"); print(df)'
python3 -c 'import pandas as pd; df = pd.read_parquet("dataset/lerobot/data/chunk-000/file-000.parquet"); print(df)'
-->


<!-- データセットマージの方法 -->
<!-- HF_HUB_OFFLINE=1 lerobot-edit-dataset \
  --repo_id /userdir/dataset/merged_test \
  --operation.type merge \
  --operation.repo_ids "['/userdir/dataset/lerobot_bk', '/userdir/dataset/lerobot_aug0', '/userdir/dataset/lerobot_aug1', '/userdir/dataset/lerobot_aug2', '/userdir/dataset/lerobot_aug3', '/userdir/dataset/lerobot_aug4', '/userdir/dataset/lerobot_aug5', '/userdir/dataset/lerobot_aug6', '/userdir/dataset/lerobot_aug7', '/userdir/dataset/lerobot_aug8', '/userdir/dataset/lerobot_aug9', '/userdir/dataset/lerobot_aug10', '/userdir/dataset/lerobot_aug11']" \
  --push_to_hub false -->