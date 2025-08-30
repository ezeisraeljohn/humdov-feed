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
from sqlmodel import select


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


@router.get("/{post_id}", response_model=PostDetailResponse)
def get_post(post_id: int, db: Session = Depends(get_session)):
    """Get a post by ID"""
    db_post = PostService.get_post_by_id(db=db, post_id=post_id)
    if not db_post:
        return PostDetailResponse(data=None, success=False, message="Post not found")
    return PostDetailResponse(
        data=db_post, success=True, message="Post retrieved successfully"
    )


@router.get("/", response_model=PostListResponse)
def list_posts(db: Session = Depends(get_session)):
    """List all posts"""
    posts = PostService.list_posts(db=db)
    return PostListResponse(
        data=posts, success=True, message="Posts retrieved successfully"
    )
