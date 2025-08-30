"""Like endpoints: like/unlike posts"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from ...models import (
    Like,
    LikeCreate,
    LikeResponse,
    LikeDetailResponse,
    LikeListResponse,
)
from ...core.session import get_session
from ...services import LikeService

router = APIRouter(prefix="/api/v1/likes", tags=["Likes"])


@router.post(
    "/", response_model=LikeDetailResponse, status_code=status.HTTP_201_CREATED
)
def like_post(like: LikeCreate, db: Session = Depends(get_session)):
    """Like a post"""
    try:
        db_like = LikeService.create_like(db=db, like=like)
        return LikeDetailResponse(
            data=db_like, success=True, message="Post liked successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{like_id}", response_model=LikeDetailResponse)
def unlike_post(like_id: int, db: Session = Depends(get_session)):
    """Unlike a post"""
    db_like = LikeService.delete_like(db=db, like_id=like_id)
    if not db_like:
        raise HTTPException(status_code=404, detail="Like not found")
    return LikeDetailResponse(
        data=db_like, success=True, message="Post unliked successfully"
    )


@router.get("/post/{post_id}", response_model=LikeListResponse)
def get_likes_for_post(post_id: str, db: Session = Depends(get_session)):
    """Get all likes for a specific post"""
    try:
        likes = LikeService.get_likes_by_post_id(db=db, post_id=post_id)
        return LikeListResponse(
            data=likes, success=True, message="Likes retrieved successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
