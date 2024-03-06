import boto3
from tqdm import tqdm


class DownloadProgressBar(object):
    def __init__(self):
        self._progress_bar = None

    def __call__(self, bytes_amount):
        if self._progress_bar is None:
            self._progress_bar = tqdm(total=float('inf'), unit='B', unit_scale=True)
        self._progress_bar.update(bytes_amount)

    def close(self):
        if self._progress_bar:
            self._progress_bar.close()


def download_file_with_progress(bucket_name, path, destination_filename):
    s3 = boto3.client('s3')

    # S3からファイルのサイズを取得
    response = s3.head_object(Bucket=bucket_name, Key=path)
    total_size = response['ContentLength']

    progress = DownloadProgressBar()

    # tqdmを使ってプログレスバーを表示しながらファイルをダウンロード
    with tqdm(total=total_size, unit='B', unit_scale=True) as progress._progress_bar:
        s3.download_file(bucket_name, path, destination_filename, Callback=progress)

    progress.close()

def put_s3(bucket_name, file_name, file_path):
    import boto3
    s3 = boto3.client('s3')
    s3.upload_file(file_name, bucket_name, file_path)

