from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.config import Settings

engine = create_engine(Settings().sqlalchemy_url, pool_pre_ping=True, pool_recycle=1800)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
