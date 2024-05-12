#! /usr/bin/env python
import ast
import gzip
import shutil
from datetime import datetime
import random
from typing import List,  Tuple

import trafilatura
import time

import requests
import argparse


from pydantic import BaseModel
from bs4 import BeautifulSoup
from tqdm import tqdm
import glob
import os

from warcio import ArchiveIterator

from src.bq import put_bq_warcs, put_bq_failed_urls
from src.load_warc import concat_records, concat_records
from src.model.failed_warcs import FailedWarc

from src.model.warc import Warc
from src.retry import retry_decorator
from src.s3_util import download_file_with_progress

base_url = "https://data.commoncrawl.org/"
os.makedirs("tmp/data/gz", exist_ok=True)
os.makedirs("tmp/data/warc", exist_ok=True)


def download_file(url, save_path):
    response = requests.get(url, stream=True)

    if response.status_code == 200:
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=128):
                f.write(chunk)
        print(f"ファイルが正常にダウンロードされました: {save_path}")
    else:
        print(f"ファイルのダウンロードに失敗しました。ステータスコード: {response.status_code}")


def decompress_gz(gz_path, output_path, remove_gz=True, fill_blank_gz=False):
    with gzip.open(gz_path, 'rb') as f_in:
        with open(output_path, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
    print(f"{gz_path}が解凍され、{output_path}に保存されました。")
    if remove_gz:
        os.remove(gz_path)

    if fill_blank_gz:
        with open(gz_path, 'w') as f:
            f.write("")


def get_cc_path_list(path_dir="data/rest_path_list/*"):
    path_list = []
    for file_path in glob.glob(path_dir):
        print(file_path)
        with open(file_path, "r") as f:
            temp_path_list = f.readlines()

        temp_path_list = [path.strip() for path in temp_path_list]

        path_list += temp_path_list

    return path_list


def cc_path_to_urls(cc_path):
    url = base_url + cc_path
    filename = cc_path.replace("/", "_")
    gz_path = f"tmp/data/gz/{filename}"
    warc_path = f"tmp/data/warc/{filename}".replace(".gz", "")

    return url, gz_path, warc_path


def halfwidth_ratio(s):
    if len(s) == 0:  # 空の文字列の場合は0を返す
        return 0
    halfwidth_count = sum(
        1 for char in s
        if '\u0020' <= char <= '\u007E' or  # 基本的なASCII範囲
        '\uFF61' <= char <= '\uFF9F' or  # 半角カタカナ
        char in ('\u0009', '\u000A', '\u000D')  # タブ、改行、復帰
    )
    return halfwidth_count / len(s)


def pre_clean(soup):
    texts_with_tags = []
    for tag in soup.find_all(True):
        # 特定のタグを除外する場合
        # if tag.name not in ['html', 'body', 'ul']:
        text = tag.get_text(separator="\n", strip=True)
        spl_text = text.split("\n")
        spl_text = [i.strip() for i in spl_text if i.strip()]  # 空の文字列を除外
        for item in spl_text:
            if tag.name == "script" or tag.name == "style":
                continue
            texts_with_tags.append((item, tag.name))  # テキストとタグの名前をタプルとして追加
    return texts_with_tags

def contains_hiragana(text: str) -> bool:
    return any("\u3040" <= char <= "\u309F" for char in text)


def extract_japanese_from_warc(path,
                               save_dir="json",
                               max_num=10 ** 10,
                               ):
    ja_soup_list = []
    path = path.replace("\\", "/")  # for windows env
    filename = path.split("/")[-1].replace(".warc", ".json")
    if os.path.exists(f"{save_dir}/{filename}"):
        print("already done")
        return
    # 途中から再開する用の位置情報の取得
    if len(ja_soup_list) > 0:
        fin_record_id = ja_soup_list[-1]["record_id"]
    else:
        fin_record_id = 0
    # WARCファイルを開く
    record_id = 0
    # どれだけjaの数をしたか
    with open(path, 'rb') as stream:
        for record in tqdm(ArchiveIterator(stream)):
            url = record.rec_headers.get_header("WARC-Target-URI")
            if url is None:
                continue
            try:
                record_id += 1
                if record_id <= fin_record_id:
                    continue
                if record.rec_type == 'response':
                    if record.http_headers.get_header('Content-Type') == 'text/html':
                        content = record.content_stream().read()

                        soup = BeautifulSoup(content, 'lxml')
                                    # 画像やpdfは除外
                        if url.endswith(".pdf") or url.endswith(".jpg") or url.endswith(".png") or url.endswith(
                                ".jpeg"):
                            continue
                        # 日本語が含まれているかどうか
                        if contains_hiragana(content.decode("utf-8", errors="ignore")):
                            extracted_text = trafilatura.extract(content.decode("utf-8", errors="ignore"),
                                                                 include_formatting=True)
                            if extracted_text is not None and contains_hiragana(extracted_text):
                                texts = pre_clean(soup)
                                pre_cleaned_text = concat_records(texts)

                                if len(texts) == 0:
                                    continue

                                if soup.title is not None:
                                    title = soup.find('title').text
                                else:
                                    title = "no_title"

                                d = {
                                        "record_id": record_id,
                                        "url": record.rec_headers.get_header('WARC-Target-URI'),
                                        "title": title,
                                        # "timestamp": record.rec_headers.get_header('WARC-Date'),
                                        "pre_cleaned_text": pre_cleaned_text,
                                        # Todo:contentはそのままだと文字化けしているのでdecodeする
                                        "html": str(content),
                                        "trafilatura_content": str(extracted_text)
                                    }

                                ja_soup_list.append(d)

                            if len(ja_soup_list) > max_num:
                                break
            except Exception as e:
                print(e)
                print("error occured at extract_japanese_from_warc")


    return ja_soup_list


@retry_decorator(max_retries=2, delay=1)
def download_warc_file(path):
    '''cloudfrontからHTTP経由でダウンロードする'''
    url, gz_path, warc_path = cc_path_to_urls(path)

    if os.path.exists(warc_path):
        print(f"warc_pathにはファイルが存在しています")
        return warc_path
    try:
        if os.path.exists(gz_path):
            print(f"gz_pathがすでに存在します: {gz_path}")
        else:
            print("downloading " + url)
            download_file(url, gz_path)
        return warc_path
    except Exception as e:
        print(e)
        print("fail loading " + url)
        return warc_path


def download_and_parse(cc_path, base_dir=None):
    # warcファイルのダウンロード
    # DOWNLOAD_MODE = os.environ.get("DOWNLOAD_MODE", "http")
    DOWNLOAD_MODE = "s3"
    # download warc file
    time_to_sleep = random.randint(2, 5)
    if DOWNLOAD_MODE == "http":
        print("downloading mode with http ")

        time.sleep(time_to_sleep)
        warc_path = download_warc_file(cc_path)
    elif DOWNLOAD_MODE == "s3":
        # awsで使用する時は環境変数にDOWNLOAD_MODE=s3を設定する。
        print("downloading mode with s3 ")
        try:
            warc_path = download_warc_file_with_s3(cc_path)
            time.sleep(time_to_sleep)

        except Exception as e:
            time.sleep(time_to_sleep)

            warc_path = download_warc_file(cc_path)

    else:
        raise ValueError("DOWNLOAD_MODE is not defined.please set environment DOWNLOAD_MODE=http or s3")

    print(warc_path)
    # ファイル関連の処理
    os.makedirs(base_dir, exist_ok=True)

    try:
        tag_records = extract_japanese_from_warc(warc_path)

        is_error = False
        error_text = ""
    except Exception as e:
        tag_records = []
        is_error = True
        print(e)
        error_text = str(e)
    # 保存用のdictを作製
    save_dict = {
        "tag_records": tag_records,
        "is_error": is_error,
        "cc_path": cc_path,
        "warc_path": warc_path,
        "error_text": error_text
    }
    # delete warc path file
    # file容量開けるため
    print(f'remove {warc_path}')
    os.remove(warc_path)
    return save_dict
    # with gzip.open(save_gz_path, 'wt', encoding="utf-8") as zipfile:
    #    json.dump(save_dict, zipfile, indent=2, ensure_ascii=False)


class TagRecord(BaseModel):
    record_id: int
    url: str
    title: str
    timestamp: datetime
    text: List[Tuple[str, str]]


class SaveDict(BaseModel):
    tag_records: List[TagRecord]
    is_error: bool
    cc_path: str
    warc_path: str
    error_text: str


def curation(target_path_list,batch_id):
    # CloudRunの環境変数から取得

    N_BATCH = 3
    cloud_run_task_idx = int(os.environ.get("CLOUD_RUN_TASK_INDEX",1))
    print(f"cloud_run_task_idx == {cloud_run_task_idx}")
    task_list = target_path_list[cloud_run_task_idx*N_BATCH:(cloud_run_task_idx+1)*N_BATCH]

    print(f"task_list == {task_list}")
    for cc_path in tqdm(task_list):
        warcs = []
        try:
            save_dict = download_and_parse(cc_path, f"process/batch")
            print(save_dict)
            if save_dict["is_error"]:
                pass
            else:
                for tag_record in save_dict["tag_records"]:
                    try:

                        if tag_record["title"] == "":
                            title = "no_title"
                        else:
                            title = tag_record["title"]

                        pre_cleaned_text = tag_record["pre_cleaned_text"]
                        record_id = tag_record["record_id"]
                        url = tag_record["url"]
                        # timestamp = tag_record["timestamp"]
                        html_text = tag_record["html"]
                        trafilatura_content = tag_record["trafilatura_content"]
                        warc = Warc(
                            record_id=record_id,
                            url=url,
                            title=title,
                            pre_cleaned_text=pre_cleaned_text,
                            html_text=html_text,
                            path=cc_path,
                            batch_number=batch_id,
                            trafilatura_content=trafilatura_content
                        )
                        warcs.append(warc)

                    except Exception as e:
                        print(e)
                        print("error occured at save warc")
            put_bq_warcs(warcs)
        except Exception as e:
            failed_url = FailedWarc(
                error_message=str(e),
                warc_path=cc_path,
                batch_number=batch_id
            )
            put_bq_failed_urls(failed_url)

def main(target_path_list,batch_id):

    try:

        # batchの番号に従って,データの処理
        curation(target_path_list,batch_id)
    except Exception as e:
        print(e)



@retry_decorator(max_retries=2, delay=1)
def download_warc_file_with_s3(path):
    url, gz_path, warc_path = cc_path_to_urls(path)

    if os.path.exists(warc_path):
        print(f"warc_pathにはファイルが存在しています")
        return warc_path

    try:
        CC_BUCKET_NAME = "commoncrawl"
        print(f'download from s3://{CC_BUCKET_NAME}/{path} to {warc_path}')
        # s3からダウンロードする設定
        download_file_with_progress(CC_BUCKET_NAME, path, warc_path)
        print(f'warc:{warc_path}のダウンロードが完了しました')
        return warc_path

    except Exception as e:
        print(e)
        print("fail loading " + url)
        raise e




if __name__ == "__main__":
    time_to_sleep = random.randint(2, 5)
    time.sleep(time_to_sleep)

    parser = argparse.ArgumentParser()
    parser.add_argument("target_path_list", type=str, help="target_path_list")
    # parser.add_argument("batch_number", type=int, help="batch_number")
    args = parser.parse_args()


    input_target_list = args.target_path_list
    # target_path_list = ast.literal_eval(input_target_list).split("+")
    # batch_number = args.batch_number

    target_path_list = input_target_list.split("+")
    print(f"length of target_path_list is {len(target_path_list)}")
    for t in target_path_list:
        print(t)
    # batch_number = int(batch_number)
    batch_number = 1

    print(f"target_path_list is {target_path_list}")
    print(f"batch_number is {batch_number}")

    main(target_path_list,batch_number)