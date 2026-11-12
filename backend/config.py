"""Shared environment configuration; importing modules does not connect to services."""
from typing import Literal

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    mysql_host: str = "127.0.0.1"
    mysql_port: int = 3306
    mysql_database: str = "taskflow"
    mysql_user: str = "taskflow"
    mysql_password: SecretStr = SecretStr("taskflow_dev")
    database_url: SecretStr | None = None
    mcp_host_url: str = "http://127.0.0.1:8000/mcp"
    mcp_transport: Literal["sse", "streamable_http"] = "sse"
    llm_model: str = "openai:gpt-4o-mini"
    openai_api_key: SecretStr | None = None
    openai_base_url: str | None = None

    @property
    def sqlalchemy_url(self) -> URL:
        if self.database_url is not None:
            from sqlalchemy.engine import make_url
            url = make_url(self.database_url.get_secret_value())
            if url.drivername != "mysql+pymysql":
                raise ValueError("DATABASE_URL must use mysql+pymysql")
            return url
        return URL.create(
            "mysql+pymysql", username=self.mysql_user,
            password=self.mysql_password.get_secret_value(), host=self.mysql_host,
            port=self.mysql_port, database=self.mysql_database,
            query={"charset": "utf8mb4"},
        )
