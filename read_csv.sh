#!/bin/bash

# CSVファイルのパスを指定
file="data/rest_path2/rest_path2.csv"



# 読み込む行の範囲を指定
start_line=1  # 開始行番号
end_line=20   # 終了行番号

# 配列を初期化
declare -a lines

# 指定された範囲の行を読み込み、配列に保存
current_line=0
while IFS= read -r line; do
    ((current_line++))
    if ((current_line >= start_line && current_line <= end_line)); then
        lines+=("$line")
    fi
done < "$file"

# チャンクの数を指定
chunk_size=4
REGIONS=( "us-central1" "us-east1" "us-west1" "us-east4")
NAMES=("crawler-uscentral" "crawler2" "crawler-uswest" "crawler-useast4" )
#TASK=(80 250 80 80)
TASK=(10 10 10 10)
launch() {
    local target_batch_list=$1
    local region=$2
    local name=$3
    local task=$4
    echo "$target_batch_list" "$region" "$name" "$task"

    sh launch.sh "$target_batch_list" "$region" "$name" "$task"
}

# 読み込んだデータをn個のjobに分割
total_lines=${#lines[@]}
job_size=$(( (total_lines +chunk_size - 1) / chunk_size ))  # 切り上げ計算

# 各チャンクを処理
for (( i=0; i<total_lines; i+=job_size )); do
    job=("${lines[@]:i:job_size}")

    # chunk内の各要素に対してクォーテーションを付けて、カンマで結合し、全体をブラケットで囲む
    printf -v joined_chunk '"%s",' "${job[@]}"
    # 末尾の余分なカンマを削除
    joined_chunk="${joined_chunk%,}"
    target_batch_list="[$joined_chunk]"

#    launch "$target_batch_list" "${REGIONS[$job_index]}" "${NAMES[$job_index]}" "${TASK[$job_index]}"
#Todo fix this
python main.py "$target_batch_list" "${REGIONS[$job_index]}" "${NAMES[$job_index]}" "${TASK[$job_index]}"


done