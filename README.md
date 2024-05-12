## 実行の流れ
## GCPの設定
```sh
gcloud auth login

```

## shell.shの実行
1. BATCH_NUMBERを設定する。

```sh
sh shell.sh

```

job_idx　を0から3まで変更することで、それぞれのジョブを実行することができる。

sh shell.shを実行後は
data/job/{実行時間}.csvにジョブの実行結果が保存される。

data/rest/rest_path2.csv空実行したパスを削除する。
