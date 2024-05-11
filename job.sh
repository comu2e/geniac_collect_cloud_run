#!/bin/bash

# 定義済みのリージョンと名前
#REGIONS=("us-east1" "us-central1" "us-west1" "us-east4")
#NAMES=("crawler2" "crawler-uscentral" "crawler-uswest" "crawler-useast4")

REGIONS=( "us-central1" "us-east1" "us-west1" "us-east4")
NAMES=("crawler-uscentral" "crawler2" "crawler-uswest" "crawler-useast4" )
#TASK=(80 250 80 80)
TASK=(10 10 10 10)

# launch関数
launch() {
    local batch=$1
    local region=$2
    local name=$3
    local task=$4
    local job_index=$5
    local batch_range=$6
    echo "$batch" "$region" "$name" "$task" $job_index $batch_range

    sh launch.sh "$batch" "$region" "$name" "$task" "$job_index" "$batch_range"
}

# 100から2002までループし、各バッチでリージョンと名前を繰り返す

BATCH_START=11
BATCH_END=12
#BATCH_RANGE=$BATCH_END-$BATCH_START-1
BATCH_RANGE=$((BATCH_END - BATCH_START ))
region_count=${#REGIONS[@]}

for (( batch=$BATCH_START; batch<=$BATCH_END; batch++ )); do
    # インデックスを使ってREGIONSとNAMESを順番に取得する
    job_index=$(( (batch - BATCH_START) % region_count ))
    launch "$batch" "${REGIONS[$job_index]}" "${NAMES[$job_index]}" "${TASK[$job_index]}" "${job_index}" "${BATCH_RANGE}"
done