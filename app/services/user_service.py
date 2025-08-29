from ..models import User, UserCreate, UserUpdate
from sqlmodel import select, Session


class UserService:
    """Service class for user-related operations"""

    @staticmethod
    def get_user_by_id(db: Session, user_id: int):
        """Retrieve a user by their ID"""
        return db.get(User, user_id)

    @staticmethod
    def create_user(db: Session, user: UserCreate) -> User:
        """Create a new user"""
        db_user = User.model_validate(user)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    @staticmethod
    def update_user(db: Session, user_id: int, user: UserUpdate) -> User | None:
        """Update an existing user"""
        db_user = db.get(User, user_id)
        if not db_user:
            return None
        user_data = user.model_dump(exclude_unset=True)
        for key, value in user_data.items():
            setattr(db_user, key, value)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    @staticmethod
    def delete_user(db: Session, user_id: int):
        """Delete a user by their ID"""
        db_user = db.get(User, user_id)
        if not db_user:
            return None
        db.delete(db_user)
        db.commit()
        return db_user
