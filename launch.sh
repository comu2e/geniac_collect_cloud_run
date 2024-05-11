#!/bin/bash

# Cloud Runサービスの名前
BATCH_NUMBER=$1
REGION=$2
SERVICE_NAME=$3
TASK_NUMBER=$4
JOB_IDX=$5
BATCH_RANGE=$6
# 初期のbatch_number
    # ジョブを非同期で起動するコマンドを実行
gcloud run jobs execute $SERVICE_NAME \
     --args "$BATCH_NUMBER,$JOB_IDX,$BATCH_RANGE"  \
     --region=$REGION \
     --tasks=$TASK_NUMBER \
    # batch_numberを1増やす
