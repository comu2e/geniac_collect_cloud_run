#!/bin/bash

# Cloud Runサービスの名前
TARGET_BATCH_LIST=$1
REGION=$2
SERVICE_NAME=$3
TASK_NUMBER=$4
# 初期のbatch_number
    # ジョブを非同期で起動するコマンドを実行
gcloud run jobs execute $SERVICE_NAME \
     --args "$TARGET_BATCH_LIST" \
     --region=$REGION \
     --tasks=$TASK_NUMBER \
    # batch_numberを1増やす
