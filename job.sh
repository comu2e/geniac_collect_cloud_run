#!/bin/bash

# 定義済みのリージョンと名前
#REGIONS=("us-east1" "us-central1" "us-west1" "us-east4")
#NAMES=("crawler2" "crawler-uscentral" "crawler-uswest" "crawler-useast4")

REGIONS=("us-east1" "us-central1" "us-west1" "us-east4")
NAMES=("crawler2" "crawler-uscentral" "crawler-uswest" "crawler-useast4")
#TASK=(80 250 80 80)
TASK=(1 1 1 1)

# launch関数
launch() {
    local batch=$1
    local region=$2
    local name=$3
    local task=$4
    sh launch.sh "$batch" "$region" "$name" "$task"
    echo "$batch" "$region" "$name" "$task"
}

# 100から2002までループし、各バッチでリージョンと名前を繰り返す
BATCH_START=20
BATCH_END=25
region_count=${#REGIONS[@]}

for (( batch=$BATCH_START; batch<=$BATCH_END; batch++ )); do
    # インデックスを使ってREGIONSとNAMESを順番に取得する
    index=$(( (batch - BATCH_START) % region_count ))
    launch "$batch" "${REGIONS[$index]}" "${NAMES[$index]}" "${TASK[$index]}"
done