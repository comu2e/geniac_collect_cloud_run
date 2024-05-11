from __future__ import annotations

from pydantic import BaseModel, UUID4
from datetime import datetime


class FailedWarc(BaseModel):
    error_message: str
    warc_path: str
    batch_number: int

    def __init__(self, **data):
        super().__init__(**data)


