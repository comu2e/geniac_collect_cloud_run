from __future__ import annotations

from pydantic import BaseModel, UUID4
from datetime import datetime

from src.repository.counter_ja_table import CounterTable
from src.repository.sqLbase import session_scope
from src.repository.warc_table import WarcTable


class Counter(BaseModel):
    id: UUID4
    path:str
    ja_count:int
    all_count:int


    def __init__(self, **data):
        super().__init__(**data)

    def uploaded(self):
        self.upload_at = datetime.now()
        return self


class CounterRepository:
    def __init__(self):
        print("CounterRepository")
    @staticmethod
    def save(counter: Counter) -> Counter:
        with session_scope() as session:
            code = CounterTable(**counter.model_dump())
            session.merge(code)
            return counter


