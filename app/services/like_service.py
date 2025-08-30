"""Like service module"""

from ..models import Like, LikeCreate, LikeUpdate
from sqlmodel import Session, select


class LikeService:
    """Service class for like-related operations"""

    @staticmethod
    def get_like_by_id(db: Session, like_id: str):
        """Retrieve a like by its ID"""
        return db.get(Like, like_id)

    @staticmethod
    def create_like(db: Session, like: LikeCreate) -> Like:
        """Create a new like"""
        db_like = Like.model_validate(like)
        db.add(db_like)
        db.commit()
        db.refresh(db_like)
        return db_like

    @staticmethod
    def update_like(db: Session, like_id: str, like: LikeUpdate) -> Like | None:
        """Update an existing like"""
        db_like = db.get(Like, like_id)
        if not db_like:
            return None
        like_data = like.model_dump(exclude_unset=True)
        for key, value in like_data.items():
            setattr(db_like, key, value)
        db.add(db_like)
        db.commit()
        db.refresh(db_like)
        return db_like

    @staticmethod
    def delete_like(db: Session, like_id: int):
        """Delete a like by its ID"""
        db_like = db.get(Like, like_id)
        if not db_like:
            return None
        db.delete(db_like)
        db.commit()
        return db_like

    @staticmethod
    def get_likes_by_post_id(db: Session, post_id: str) -> list[Like]:
        """Retrieve all likes for a specific post"""
        statement = select(Like).where(Like.post_id == post_id)
        results = db.exec(statement)
        return list(results.all())
