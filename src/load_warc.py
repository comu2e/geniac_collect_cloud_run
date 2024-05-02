
from typing import List, Tuple
import os

def concat_records(tag_records: List[Tuple[str, str]]):
    annotate_text_length = 100
    # タグで分割されているテキストを連結

    concat_records =  ''.join([t[0] for t in tag_records])
    return concat_records

