from sqlalchemy import Column, DateTime, String, UUID, Integer
from src.config import Config
from src.repository.sqLbase import Base, metadata, engine

config = Config()

# ターゲットとする特許のテーブル定義
class CounterTable(Base):

    __tablename__ = "counter"
    id = Column(UUID, primary_key=True)
    path = Column(String)
    ja_count= Column(Integer)
    all_count = Column(Integer)



    @staticmethod
    def drop_table() -> None:
        table = metadata.tables.get(CounterTable.__tablename__)
        if table is not None:
            CounterTable.__table__.drop(engine, checkfirst=True)
