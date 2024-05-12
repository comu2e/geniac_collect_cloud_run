#!/bin/bash

# 開始行番号と終了行番号を計算
batch_number=1
# フォーマットしたデータを表示
REGIONS=( "us-central1" "us-east1" "us-west1" "us-east4")
JOB_NAMES=("crawler-uscentral" "crawler2" "crawler-uswest" "crawler-useast4" )
TASK_COUNTS=(200 150 150 150)

N_BATCH=3
# どこのリージョンで行うかを設定する
job_idx=2

REGION=${REGIONS[$job_idx]}
JOB_NAME=${JOB_NAMES[$job_idx]}
TASK=${TASK_COUNTS[$job_idx]}

# バッチ処理の数を指定
printf "batch_number: $batch_number\n"
printf "region: $REGION\n"
printf "job_name: $JOB_NAME\n"
printf "task: $TASK\n"

# start line and end line
start_line=$((TASK * (batch_number - 1) + 1))
end_line=$((TASK * ( batch_number - 1 + N_BATCH) + 1 ))

printf  '============'
printf "start_line: $start_line\n"
printf "end_line: $end_line\n"
printf  '============'

# CSVファイルのパスを指定
file="data/rest_path2/rest_path2.csv"

# 文字列を格納する変数を宣言
lines=''

# ファイルから指定された範囲の行を読み込み、配列に保存
#
# linesをファイルに書き込む
#　実行時間を文字列として変数に保存してファイル名にする
 now=$(date '+%Y%m%d%H%M%S')


for i in $(seq $start_line $end_line); do
  line=$(sed -n ${i}p $file)
  # +で連結する
  lines+="$line+"

  # ファイルに書き込む
  # 改行込みで書き込む
  echo $line >> "data/job/rest_path2_${now}.csv"

done

# 最後の+を削除
lines=${lines%+}


echo "$lines"
gcloud run jobs execute $JOB_NAME --args "$lines" --region=$REGION --tasks=$TASK
