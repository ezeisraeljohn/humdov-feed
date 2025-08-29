"""Post endpoints: create, read, list posts"""

from fastapi import APIRouter, Depends, status
from ...models import (
    Post,
    PostCreate,
    PostUpdate,
    PostListResponse,
    PostResponse,
    PostDetailResponse,
)
from ...core.session import Session, get_session
from ...services import PostService


router = APIRouter(prefix="/api/v1/posts", tags=["Posts"])


@router.post(
    "/", response_model=PostDetailResponse, status_code=status.HTTP_201_CREATED
)
def create_posts(post: PostCreate, db: Session = Depends(get_session)):
    """Create the post associated to a user"""
    db_post = PostService.create_post(db=db, post=post)
    return PostDetailResponse(
        data=db_post, success=True, message="Post created successfully"
    )
