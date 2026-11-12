from sqlalchemy.orm import Session


def test_get_db(mysql_engine, monkeypatch):
    from backend.server import db
    from sqlalchemy.orm import sessionmaker

    monkeypatch.setattr(db, "SessionLocal", sessionmaker(bind=mysql_engine))
    generator = db.get_db()
    session = next(generator)
    assert isinstance(session, Session)
    generator.close()
