"""The comment service file"""

from ..models import Comment, CommentCreate, CommentUpdate
from sqlmodel import Session, select


class CommentService:
    """Service class for comment-related operations"""

    @staticmethod
    def get_comment_by_id(db: Session, comment_id: str):
        """Retrieve a comment by its ID"""
        return db.get(Comment, comment_id)

    @staticmethod
    def create_comment(db: Session, comment: CommentCreate) -> Comment:
        """Create a new comment"""
        db_comment = Comment.model_validate(comment)
        try:
            db.add(db_comment)
            db.commit()
            db.refresh(db_comment)
        except:
            db.rollback()
            raise Exception("Failed to create db")
        return db_comment

    @staticmethod
    def update_comment(
        db: Session, comment_id: str, comment: CommentUpdate
    ) -> Comment | None:
        """Update an existing comment"""
        db_comment = db.get(Comment, comment_id)
        if not db_comment:
            return None
        comment_data = comment.model_dump(exclude_unset=True)
        for key, value in comment_data.items():
            setattr(db_comment, key, value)
        db.add(db_comment)
        db.commit()
        db.refresh(db_comment)
        return db_comment

    @staticmethod
    def delete_comment(db: Session, comment_id: str) -> Comment | None:
        """Delete a comment by its ID"""
        db_comment = db.get(Comment, comment_id)
        if not db_comment:
            return None
        db.delete(db_comment)
        db.commit()
        return db_comment

    @staticmethod
    def list_comments(db: Session) -> list[Comment]:
        """List all comments"""
        comments = db.exec(select(Comment)).all()
        return [Comment.model_validate(comment) for comment in comments]
