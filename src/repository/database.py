import os

from google.cloud.sql.connector import Connector, IPTypes
import pymysql

import sqlalchemy

def connect_with_connector() -> sqlalchemy.engine.base.Engine:

    instance_connection_name = os.environ[
        "INSTANCE_CONNECTION_NAME"
    ]
    db_user = os.environ["DB_USER"]
    db_pass = os.environ["DB_PASS"]
    db_name = os.environ["DB_NAME"]

    # ip_type = IPTypes.PRIVATE if os.environ.get("PRIVATE_IP") else IPTypes.PUBLIC

    connector = Connector()

    def getconn() -> pymysql.connections.Connection:
        conn: pymysql.connections.Connection = connector.connect(
            instance_connection_name,
            "pymysql",
            user=db_user,
            password=db_pass,
            db=db_name,
        )
        return conn

    pool = sqlalchemy.create_engine(
        url="mysql+pymysql://",
        creator=getconn,
        pool_recycle=10,
    )
    return pool
pool = connect_with_connector()
