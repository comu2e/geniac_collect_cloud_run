#!/bin/bash

# Cloud Runサービスの名前
SERVICE_NAME="crawler-uswest"
REGION="us-west1"
TASK_NUMBER=50
NUMBER=$1
# 初期のbatch_number
BATCH_NUMBER=$NUMBER

# サービスに渡すコンテナコマンドのベース

# 100から200までのbatch_numberに対してループ
for ((batch_number=$NUMBER; batch_number<=$NUMBER; batch_number++)); do
    # コンテナコマンドを生成
    CONTAINER_ARGS="$batch_number"

    # ジョブを非同期で起動するコマンドを実行
    gcloud run jobs execute $SERVICE_NAME \
     --args "$CONTAINER_ARGS"  \
     --region=$REGION \
     --tasks=$TASK_NUMBER \
    # batch_numberを1増やす
    ((BATCH_NUMBER++))
done