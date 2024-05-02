from typing import TypedDict

from google.auth import compute_engine
import google.auth.transport.requests as grequests
import boto3


class Credentials(TypedDict):
    '''AWSの一時認証情報の型定義'''
    AccessKeyId: str
    SecretAccessKey: str
    SessionToken: str
    Expiration: str


def get_aws_creds(aws_role_arn: str):
    '''Google CloudのメータデータサーバーからIDトークンを取得し、AWSの一時認証情報を取得する'''

    try:
        # Google CloudのメタデータサーバーからIDトークンを取得
        request = grequests.Request()
        g_credentials = compute_engine.IDTokenCredentials(
            request=request,
            target_audience="https://sts.amazonaws.com/",
            use_metadata_identity_endpoint=True
        )
        g_credentials.refresh(request)
        token: str = g_credentials.token

        # AWSのSTSを使って一時認証情報を取得
        sts = boto3.client('sts')
        assume_role_res = sts.assume_role_with_web_identity(
            RoleArn=aws_role_arn,
            WebIdentityToken=token,
            RoleSessionName="session",
        )
        a_credentials: Credentials = assume_role_res.get('Credentials')  # type: ignore
        return a_credentials
    except Exception as e:
        print(f"Error: {e}")
        return None
