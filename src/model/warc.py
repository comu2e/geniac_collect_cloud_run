from __future__ import annotations

from pydantic import BaseModel, UUID4
from datetime import datetime

# from src.repository.sqLbase import session_scope
# from src.repository.warc_table import WarcTable


class Warc(BaseModel):
    record_id: int
    url: str
    title: str
    pre_cleaned_text: str
    html_text: str
    path: str
    batch_number:int
    trafilatura_content: str

    def __init__(self, **data):
        super().__init__(**data)

    def uploaded(self):
        self.upload_at = datetime.now()
        return self
