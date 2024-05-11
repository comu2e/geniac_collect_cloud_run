import os

from dotenv import load_dotenv


class Config:
    is_test: bool
    db_path: str
    test_db_path: str
    echo: bool

    def __init__(self):
        # .env ファイルから環境変数を読み込む
        dotenv_path = os.path.join(os.getcwd(), ".env")
        load_dotenv(dotenv_path=dotenv_path)

        self.is_test = os.getenv("ENV") == "test"
        self.__setup_db()


    def __str_to_boolean(self, value: str) -> bool:
        return value.lower() == "true"

    def __setup_db(self):
        """
        DB の設定を読み込む
        """
        self.db_engine = os.getenv("DB_ENGINE", "")
        if self.db_engine == "sqlite":
            self.db_path = "sqlite:///" + os.getcwd() + os.getenv("DB_PATH", "")
        elif self.db_engine == "postgres":
            self.db_path = (
                "postgresql://"
                + os.getenv("DB_USER", "")
                + ":"
                + os.getenv("DB_PASSWORD", "")
                + "@"
                + os.getenv("DB_HOST", "")
                + ":"
                + os.getenv("DB_PORT", "")
                + "/"
                + os.getenv("DB_NAME", "")
            )
        elif self.db_engine == "postgresql+psycopg2":
            self.db_path = (f"{self.db_engine}://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
                            f"@{os.getenv('DB_HOST','')}/{os.getenv('DB_NAME')}"
                            f"?host=/cloudsql/{os.getenv('INSTANCE_CONNECTION_NAME','')}")
        self.test_db_path = "sqlite:///" + os.getcwd() + "/data/test.db"
        self.echo = self.__str_to_boolean(os.getenv("SQLALCHEMY_ECHO", "False"))


# 使用例
# config = Config()
# print("Is test ?", config.is_test)
# print(config.db_path)
