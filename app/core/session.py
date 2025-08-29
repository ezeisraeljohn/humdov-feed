from sqlmodel import Session, create_engine
from app.core import settings


DATABASE_URL = settings.DATABASE_URL
engine = create_engine(DATABASE_URL)


def get_session():
    """Creates a Session for a transaction"""
    with Session(engine) as session:
        yield session
