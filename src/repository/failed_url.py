from sqlalchemy import Column, DateTime, String, UUID, Integer
from src.config import Config
from src.repository.sqLbase import Base, metadata, engine

config = Config()

# ターゲットとする特許のテーブル定義
class FailedUrlTables(Base):

    __tablename__ = "failed_urls"
    id = Column(UUID, primary_key=True)
    url = Column(String)
    batch_number = Column(Integer)
    error_message = Column(String)
    created_at = Column(DateTime)



    @staticmethod
    def drop_table() -> None:
        table = metadata.tables.get(FailedUrlTables.__tablename__)
        if table is not None:
            FailedUrlTables.__table__.drop(engine, checkfirst=True)
