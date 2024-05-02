from sqlalchemy import Column, DateTime, String, UUID, Integer
from src.config import Config
from src.repository.sqLbase import Base, metadata, engine

config = Config()

# ターゲットとする特許のテーブル定義
class WarcTable(Base):

    __tablename__ = "warcs"
    id = Column(UUID, primary_key=True)
    record_id = Column(Integer)
    url = Column(String)
    title = Column(String)
    timestamp = Column(DateTime)
    pre_cleaned_text = Column(String)
    html_text = Column(String)
    path = Column(String)
    batch_number = Column(Integer)


    @staticmethod
    def drop_table() -> None:
        table = metadata.tables.get(WarcTable.__tablename__)
        if table is not None:
            WarcTable.__table__.drop(engine, checkfirst=True)
