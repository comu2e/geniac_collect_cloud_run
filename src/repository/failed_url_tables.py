from __future__ import annotations

from pydantic import BaseModel, UUID4
from datetime import datetime

from src.repository.sqLbase import session_scope


class FailedUrl(BaseModel):
    id: UUID4
    url: str
    error_message: str
    batch_number: int
    created_at: datetime

    def __init__(self, **data):
        super().__init__(**data)



class FailedUrlRepository:
    def __init__(self):
        print("FailedUrlRepository")
    @staticmethod
    def save(failed_urls: FailedUrl) -> FailedUrl:
        with session_scope() as session:
            code = FailedUrl(**failed_urls.model_dump())
            session.merge(code)
            return failed_urls


