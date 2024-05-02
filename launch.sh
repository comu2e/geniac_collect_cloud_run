#!/bin/bash

# Cloud Runサービスの名前
SERVICE_NAME="crawler"

# 初期のbatch_number
BATCH_NUMBER=100

# サービスに渡すコンテナコマンドのベース

# 100から200までのbatch_numberに対してループ
for ((batch_number=100; batch_number<=102; batch_number++)); do
    # コンテナコマンドを生成
    CONTAINER_ARGS="$batch_number"

    # ジョブを非同期で起動するコマンドを実行
    gcloud run jobs execute $SERVICE_NAME \
     --args "$CONTAINER_ARGS"  \
     --region=us-central1 \
     --async
    # batch_numberを1増やす
    ((BATCH_NUMBER++))
done