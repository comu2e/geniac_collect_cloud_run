from contextlib import contextmanager

from sqlalchemy import MetaData, create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker
from src.config import Config

# SQLAlchemyエンジンの作成
config = Config()
print(config.db_path, config.echo)

if config.is_test:
    engine = create_engine(config.test_db_path, echo=config.echo)
else:
    engine = create_engine(config.db_path, echo=config.echo)  # Trueにすると実行するSQLが表示される
Session = sessionmaker(bind=engine)

Base = declarative_base()

metadata = MetaData()
metadata.reflect(bind=engine)


@contextmanager
def session_scope():
    session = Session()
    try:
        yield session
        session.commit()
    except:
        # 例外が発生した場合はrollback()
        session.rollback()
        raise
    finally:
        session.close()
