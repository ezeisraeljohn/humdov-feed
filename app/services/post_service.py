"""Service class for post-related operations"""

from ..models import Post, PostCreate, PostUpdate
from sqlmodel import Session, select


class PostService:
    """Service class for post-related operations"""

    @staticmethod
    def get_post_by_id(db: Session, post_id: int):
        """Retrieve a post by its ID"""
        return db.get(Post, post_id)

    @staticmethod
    def create_post(db: Session, post: PostCreate) -> Post:
        """Create a new post"""
        db_post = Post.model_validate(post)
        try:
            db.add(db_post)
            db.commit()
            db.refresh(db_post)
        except:
            db.rollback()
            raise Exception("Failed to create db")
        return db_post

    @staticmethod
    def update_post(db: Session, post_id: int, post: PostUpdate) -> Post | None:
        """Update an existing post"""
        db_post = db.get(Post, post_id)
        if not db_post:
            return None
        post_data = post.model_dump(exclude_unset=True)
        for key, value in post_data.items():
            setattr(db_post, key, value)
        db.add(db_post)
        db.commit()
        db.refresh(db_post)
        return db_post

    @staticmethod
    def delete_post(db: Session, post_id: int) -> Post | None:
        """Delete a post by its ID"""
        db_post = db.get(Post, post_id)
        if not db_post:
            return None
        db.delete(db_post)
        db.commit()
        return db_post

    @staticmethod
    def list_posts(db: Session) -> list[Post]:
        """List all posts"""
        posts = db.exec(select(Post)).all()
        return [Post.model_validate(post) for post in posts]
