"""Shared MySQL fixtures; only an explicitly selected test database is cleared."""
import os

import pytest
from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session

from backend.server.models import Base


@pytest.fixture(scope="session")
def mysql_engine():
    raw_url = os.environ.get("TEST_DATABASE_URL")
    if not raw_url:
        pytest.skip("Set TEST_DATABASE_URL to a dedicated MySQL test database")
    url = make_url(raw_url)
    if url.drivername != "mysql+pymysql" or not (url.database or "").endswith("_test"):
        pytest.fail("TEST_DATABASE_URL must use mysql+pymysql and a database ending in _test")
    engine = create_engine(url, pool_pre_ping=True)
    try:
        yield engine
    finally:
        engine.dispose()


@pytest.fixture
def db(mysql_engine):
    Base.metadata.drop_all(mysql_engine)
    Base.metadata.create_all(mysql_engine)
    try:
        with Session(mysql_engine) as session:
            yield session
    finally:
        Base.metadata.drop_all(mysql_engine)
