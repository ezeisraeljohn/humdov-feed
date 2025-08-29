"""service to handle tag related operations"""

from ..models import Tag, TagCreate, TagUpdate
from sqlmodel import select, Session


class TagService:
    """Service class for tag-related operations"""

    @staticmethod
    def get_tag_by_id(db: Session, tag_id: int):
        """Retrieve a tag by its ID"""
        return db.get(Tag, tag_id)

    @staticmethod
    def create_tag(db: Session, tag: TagCreate) -> Tag:
        """Create a new tag"""
        db_tag = Tag.model_validate(tag)
        db.add(db_tag)
        db.commit()
        db.refresh(db_tag)
        return db_tag

    @staticmethod
    def update_tag(db: Session, tag_id: int, tag: TagUpdate) -> Tag | None:
        """Update an existing tag"""
        db_tag = db.get(Tag, tag_id)
        if not db_tag:
            return None
        tag_data = tag.model_dump(exclude_unset=True)
        for key, value in tag_data.items():
            setattr(db_tag, key, value)
        db.add(db_tag)
        db.commit()
        db.refresh(db_tag)
        return db_tag

    @staticmethod
    def delete_tag(db: Session, tag_id: int):
        """Delete a tag by its ID"""
        db_tag = db.get(Tag, tag_id)
        if not db_tag:
            return None
        db.delete(db_tag)
        db.commit()
        return db_tag
