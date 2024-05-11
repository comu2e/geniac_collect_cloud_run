import os

from typing import List

import pandas as pd

from src.model.failed_warcs import  FailedWarc
from src.model.warc import Warc


def put_bq_warcs(warcs:List[Warc]):
    table_id = 'hatakeyamallm.cc_dataset.warcs'
    records = [
        {
            "record_id": warc.record_id,
            "url": warc.url,
            "title": warc.title,
            "pre_cleaned_text": warc.pre_cleaned_text,
            "html_text": warc.html_text,
            "warc_path": warc.path,
            "batch_number": warc.batch_number,
            'trafilatura_content': warc.trafilatura_content,
        }
        for warc in warcs
    ]
    length_records = len(records)
    chuk_size = 8
    try:
        for i in range(0, length_records, chuk_size):
            df = pd.DataFrame(records[i:i+chuk_size])
            df.to_gbq(table_id, if_exists='append')
            print('success insert')
    except Exception as e:
        print('failed insert')
        print(e)
def put_bq_failed_urls(failedWarc:FailedWarc):
    table_id = 'hatakeyamallm.cc_dataset.failed_warcs'
    records = [
        {
            "error_message": failedWarc.error_message,
            'warc_path': failedWarc.warc_path,
            "batch_number": failedWarc.batch_number,
        }
    ]
    df = pd.DataFrame(records)
    df.to_gbq(table_id, if_exists='append')
    print('success failed warc insert')


