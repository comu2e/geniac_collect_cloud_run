#! /usr/bin/env python
import os
import glob

import gzip
import shutil
import requests
import argparse

base_url = "https://data.commoncrawl.org/"
os.makedirs("data/gz", exist_ok=True) 
os.makedirs("data/warc", exist_ok=True)

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

def get_cc_path_list(path_dir="data/path_list/*"):
    path_list = []
    for file_path in glob.glob(path_dir):
        print(file_path)
        with open(file_path, "r") as f:
            temp_path_list = f.readlines()

        temp_path_list = [path.strip() for path in temp_path_list]

        path_list += temp_path_list

    return path_list


def cc_path_to_urls(cc_path):
    url = base_url+cc_path
    filename = cc_path.replace("/", "_")
    gz_path = f"data/gz/{filename}"
    warc_path = f"data/warc/{filename}".replace(".gz", "")

    return url, gz_path, warc_path


def download_warc_file(path):
    url, gz_path, warc_path = cc_path_to_urls(path)

    if os.path.exists(warc_path):
        print(f"warc_pathにはファイルが存在しています")
        return warc_path
    try:
        if os.path.exists(gz_path):
            print(f"gz_pathがすでに存在します: {gz_path}")
        else:
            print("downloading "+url)
            download_file(url, gz_path)
        print("decompressing "+gz_path)
        decompress_gz(gz_path, warc_path,
                      remove_gz=False, fill_blank_gz=True)
        return warc_path
    except Exception as e:
        print(e)
        print("fail loading "+url)
        return warc_path

from warcio.archiveiterator import ArchiveIterator
from bs4 import BeautifulSoup
from tqdm import tqdm
import json
import glob
import os

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


def extract_japanese_from_warc(path,
                               save_dir="json",
                               max_num=10**10,
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
    with open(path, 'rb') as stream:
        for record in tqdm(ArchiveIterator(stream)):
            record_id += 1
            if record_id <= fin_record_id:
                continue
            if record.rec_type == 'response':
                if record.http_headers.get_header('Content-Type') == 'text/html':
                    content = record.content_stream().read()
                    soup = BeautifulSoup(content, 'html.parser')
                    # <html>タグからlang属性を取得
                    html_tag = soup.find('html')
                    if html_tag and html_tag.has_attr('lang'):
                        lang = html_tag['lang']
                        texts = pre_clean(soup)
                        if len(texts) == 0:
                            continue
                        if lang == "ja":
                            if soup.title is not None:
                                title = soup.title.string
                            else:
                                title = ""
                            d = {
                                "record_id": record_id,
                                "url": record.rec_headers.get_header('WARC-Target-URI'),
                                "title": title,
                                "timestamp": record.rec_headers.get_header('WARC-Date'),
                                "text": texts,
                            }
                            ja_soup_list.append(d)
                        if len(ja_soup_list) > max_num:
                            break
    return ja_soup_list

def download_and_parse(cc_path, base_dir=None):
    # warcファイルのダウンロード
    warc_path = download_warc_file(cc_path)
    # ファイル関連の処理
    os.makedirs(base_dir, exist_ok=True)
    # パス関連の処理
    file_name = os.path.basename(warc_path)
    base_name = os.path.splitext(file_name)[0]
    file_base_name = "_".join(base_name.split("_")[2:])
    if base_dir is None:
        base_dir = "/tmp/"
    save_gz_path = f"{base_dir}/{file_base_name}_japanese.json.gz"
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
      "tag_records" : tag_records,
      "is_error" : is_error,
      "cc_path" : cc_path,
      "warc_path" : warc_path,
      "error_text" : error_text
    }
    with gzip.open(save_gz_path, 'wt', encoding="utf-8") as zipfile:
       json.dump(save_dict, zipfile, indent=2, ensure_ascii=False)


def curation(batch_number, submit_dir="/content/submit", is_debug=False):
    s3_bucket_name = os.environ.get('S3_BUCKET_NAME')
    print(s3_bucket_name)

    cc_path_list = get_cc_path_list()
    if is_debug:
        n_batch = 1
    else:
        n_batch = 10
    start_idx, end_idx = batch_number * n_batch, (batch_number+1) * n_batch
    target_path_list  = cc_path_list[start_idx:end_idx]
    for cc_path in tqdm(target_path_list):
        download_and_parse(cc_path, f"process/batch{batch_number}")
    shutil.make_archive(f'{submit_dir}/{batch_number}',
                        format='zip', root_dir=f"process/batch{batch_number}")

    put_s3(s3_bucket_name, f"{submit_dir}/{batch_number}.zip", f"{batch_number}.zip")
    shutil.rmtree("process/")


def put_s3(bucket_name, file_name, file_path):
    import boto3
    s3 = boto3.client('s3')
    s3.upload_file(file_name, bucket_name, file_path)

def main(batch_number):
    """
    download path list from commoncrawl
    """
    # Parameter
    # 今回処理するwarcのパスリストが圧縮されているURL
    # CC-MAIN-2023-50以外にも存在するが, 一旦このURLのみで行う
    path_urls = [
        "https://data.commoncrawl.org/crawl-data/CC-MAIN-2023-50/warc.paths.gz",
    ]
    # パスリストをダウンロードするフォルダの作成
    os.makedirs("data", exist_ok=True)
    os.makedirs("data/path_list", exist_ok=True)
    os.makedirs("data/path_list", exist_ok=True)

    # Process
    # Parameterで指定したURLからパス(gz)をダウンロードし,解凍する
    for url in path_urls:
        file_name = url.split("/")[-2]+".gz"
        try:
            # パスリストが格納されているgzファイルをdata_list配下に保存
            download_file(url, f"data/path_list/{file_name}")
            # 保存されたgzファイルを解凍する
            decompress_gz(f"data/path_list/{file_name}",
                        f"data/path_list/{os.path.splitext(file_name)[0]}")
        except:
            pass
    # Process
    # 保存されているwarcファイルのパスのリストを取得
    cc_paths = get_cc_path_list(path_dir="data/path_list/*")
    # 表示
    cc_paths

    # ここの番号を指定を受けた番号に変更をしてください
    # is_debug = True
    is_debug = os.environ.get('IS_DEBUG', "False")
    if is_debug == "True":
        is_debug = True
    else:
        is_debug = False
    if is_debug:
        print("デバッグモードで実行します")
    else:
        print("本番モードで実行します")

    # 保存用ディレクトリの指定
    # submit_dir = "submit"
    # もしdriveがマウントできれば,上のsubmit_dirをコメントアウト, 以下をコードにしてください.
    submit_dir = "submit"

    # batchの番号に従って,データの処理
    curation(batch_number, submit_dir=submit_dir, is_debug=is_debug)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("batch_number", type=int, help="batch_number")
    args = parser.parse_args()
    print(args.batch_number)
    main(args.batch_number)