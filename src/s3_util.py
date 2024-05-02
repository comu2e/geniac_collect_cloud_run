import boto3
from tqdm import tqdm
from src.aws import Credentials, get_aws_creds
from boto3.session import Session
import os

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

    AWS_ROLE_ARN = os.environ.get("ROLE_ARN","arn:aws:iam::369149519541:role/iam-gcp-s3-get")
    print(f"aws role arn: {AWS_ROLE_ARN}")
    creds = get_aws_creds(AWS_ROLE_ARN) if AWS_ROLE_ARN else None
    session: Session = Session(
        aws_access_key_id=creds.get("AccessKeyId"),
        aws_secret_access_key=creds.get("SecretAccessKey"),
        aws_session_token=creds.get("SessionToken"),
    ) if creds else Session()

    s3 = session.client('s3')

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
