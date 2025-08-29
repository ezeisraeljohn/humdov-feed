"""Like SQLModel definition and API schemas"""

from sqlmodel import Field, SQLModel
from typing import Optional
from datetime import datetime
from uuid import UUID, uuid4
from sqlmodel import Relationship


class Base(SQLModel):
    """Base schema with common fields"""

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class UserCreate(Base):
    """Schema for creating a new user"""

    username: str
    full_name: Optional[str] = None


class UserUpdate(UserCreate):
    """Schema for updating user information"""


class User(UserUpdate, table=True):
    """SQLModel for the User table"""

    __tablename__ = "users"

    posts: list["Post"] = Relationship(back_populates="user")
    likes: list["Like"] = Relationship(back_populates="user")


class UserResponse(SQLModel):
    """Schema for user response"""

    id: UUID
    created_at: datetime
    updated_at: datetime
    username: str
    full_name: Optional[str] = None


class UserDetailResponse(SQLModel):
    """Schema for detailed user response"""

    data: User
    success: bool = True
    message: str = "User retrieved successfully"


class UserListResponse(SQLModel):
    """Schema for list of users response"""

    data: list[UserResponse]
    success: bool = True
    message: str = "Users retrieved successfully"


class PostCreate(Base):
    """Schema for creating a new post"""

    author_id: UUID = Field(foreign_key="users.id")
    title: str
    body: str


class PostUpdate(PostCreate):
    """Schema for updating post information"""


class Post(PostUpdate, table=True):
    """SQLModel for the Post table"""

    __tablename__ = "posts"
    user: Optional["User"] = Relationship(back_populates="posts")
    likes: list["Like"] = Relationship(back_populates="post")


class PostResponse(SQLModel):
    """Schema for post response"""

    id: UUID
    created_at: datetime
    updated_at: datetime
    author_id: UUID
    title: str
    body: str


class PostDetailResponse(SQLModel):
    """Schema for detailed post response"""

    data: Post
    success: bool = True
    message: str = "Post retrieved successfully"


class PostListResponse(SQLModel):
    """Schema for list of posts response"""

    data: Optional[list[PostResponse]]
    success: bool = True
    message: str = "Posts retrieved successfully"


class LikeCreate(Base):
    """Schema for creating a new like"""

    user_id: UUID = Field(foreign_key="users.id")
    post_id: UUID = Field(foreign_key="posts.id")


class LikeUpdate(LikeCreate):
    """Schema for updating like information"""


class Like(LikeUpdate, table=True):
    """SQLModel for the Like table"""

    __tablename__ = "likes"

    user: Optional["User"] = Relationship(back_populates="likes")
    post: Optional["Post"] = Relationship(back_populates="likes")


class LikeResponse(SQLModel):
    """Schema for like response"""

    id: UUID
    created_at: datetime
    updated_at: datetime
    user_id: UUID
    post_id: UUID


class LikeListResponse(SQLModel):
    """Schema for list of likes response"""

    data: list[LikeResponse]
    success: bool = True
    message: str = "Likes retrieved successfully"


class TagCreate(Base):
    """Schema for creating a new tag"""

    post_id: UUID
    tag: str = Field(index=True, unique=True)


class TagUpdate(TagCreate):
    """Schema for updating tag information"""


class Tag(TagUpdate, table=True):
    """SQLModel for the Tag table"""

    __tablename__ = "tags"


class TagResponse(SQLModel):
    """Schema for tag response"""

    id: UUID
    created_at: datetime
    updated_at: datetime
    tag: str


class TagListResponse(SQLModel):
    """Schema for list of tags response"""

    data: list[TagResponse]
    success: bool = True
    message: str = "Tags retrieved successfully"


class PostTagCreate(Base):
    post_id: UUID = Field(foreign_key="posts.id")
    tag_id: UUID = Field(foreign_key="tags.id")


class PostTagUpdate(PostTagCreate):
    """Schema for updating post-tag relationship"""


class PostTag(PostTagUpdate, table=True):
    """SQLModel for the PostTag table"""

    __tablename__ = "post_tags"
