"""Database engine and session setup"""

from .session import engine
from sqlmodel import SQLModel

from ..models.models import User, Post, Like, Tag


def init_db():
    """Create the database tables."""
    SQLModel.metadata.create_all(engine)


init_db()
