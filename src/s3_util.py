import boto3
from tqdm import tqdm
from src.aws import Credentials, get_aws_creds
from boto3.session import Session
import os

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

    # tqdmを使ってプログレスバーを表示しながらファイルをダウンロード
    s3.download_file(bucket_name, path, destination_filename)



