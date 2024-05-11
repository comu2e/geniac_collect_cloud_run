from __future__ import annotations

from pydantic import BaseModel

class Counter(BaseModel):
    path:str
    ja_count:int
    meta_ja_count:int
    all_count:int

