## 実行の流れ

# ジョブの実行

## GCPの設定

1. cloudrunのサービスアカウントを作成し、権限を付与する。

2. 下記コマンドを実行して認証する
```sh
gcloud auth login
```

上記作成したサービスアカウントjsonで認証する場合は下記コマンドを実行する
```sh
gcloud auth login --cred-file=service-account.json
```

## コンテナイメージのpush

1. コンテナイメージをビルドする

```sh
sh artifact_push.sh
```



## run_cloudrun_job.shの実行

このシェルスクリプトは、特定のリージョンで特定のGoogle Cloud Runジョブを実行するためのものです。
スクリプトはバッチ番号を元に、 CSVファイルからデータの特定範囲を読み取り、
そのデータを用いてクラウドジョブを実行します。

cloud run jobで実行するコマンドは、main.pyの引数を変更することで変更できます。

main.pyの引数をrest_path2のファイルから読み取って引数としてpython main.pyに渡しています。
```sh
python main.py target_list='crawl-data/CC_MAINxxx+crawl-data/CC_MAINyyy']
```


2. BATCH_NUMBERを設定する。

```sh
sh run_cloudrun_job.sh

```
