from sqlalchemy.dialects import mysql
from sqlalchemy.schema import CreateTable

from backend.config import Settings
from backend.server.models import Item


def test_mysql_url_handles_special_password_characters():
    settings = Settings(_env_file=None, database_url=None, mysql_password="p@ss:/?#中文")
    url = settings.sqlalchemy_url
    assert url.drivername == "mysql+pymysql"
    assert url.password == "p@ss:/?#中文"
    assert url.query["charset"] == "utf8mb4"


def test_schema_compiles_for_mysql():
    ddl = str(CreateTable(Item.__table__).compile(dialect=mysql.dialect()))
    assert "VARCHAR(255)" in ddl
    assert "TEXT" in ddl
