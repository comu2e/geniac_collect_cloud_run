#!/bin/bash

# 定義済みのリージョンと名前
REGIONS=("us-east1" "us-central1" "us-west1")
NAMES=("crawler2" "crawler-uscentral" "crawler-uswest")

# launch関数
launch() {
    local batch=$1
    local region=$2
    local name=$3
    sh launch.sh "$batch" "$region" "$name"
    echo "$batch" "$region" "$name"
}

# 100から2002までループし、各バッチでリージョンと名前を繰り返す
BATCH_START=24
BATCH_END=36
region_count=${#REGIONS[@]}

for (( batch=$BATCH_START; batch<=$BATCH_END; batch++ )); do
    # インデックスを使ってREGIONSとNAMESを順番に取得する
    index=$(( (batch - BATCH_START) % region_count ))
    launch "$batch" "${REGIONS[$index]}" "${NAMES[$index]}"
done