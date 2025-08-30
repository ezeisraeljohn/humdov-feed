"""Comements API Router"""

from fastapi import APIRouter, HTTPException, status, Depends
from sqlmodel import Session
from ...models import (
    Comment,
    CommentCreate,
    CommentUpdate,
    CommentResponse,
    CommentDetailResponse,
    CommentListResponse,
)
from ...core.session import get_session
from ...services import CommentService

router = APIRouter(prefix="/api/v1/comments", tags=["Comments"])


@router.post(
    "/", response_model=CommentDetailResponse, status_code=status.HTTP_201_CREATED
)
def create_comment(comment: CommentCreate, db: Session = Depends(get_session)):
    """Create a new comment"""
    try:
        db_comment = CommentService.create_comment(db=db, comment=comment)
        return CommentDetailResponse(
            data=db_comment, success=True, message="Comment created successfully"
        )
    except Exception as e:
        print(e)
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{comment_id}", response_model=CommentDetailResponse)
def get_comment(comment_id: str, db: Session = Depends(get_session)):
    """Get a comment by ID"""
    db_comment = CommentService.get_comment_by_id(db=db, comment_id=comment_id)
    if not db_comment:
        return CommentDetailResponse(
            data=None, success=False, message="Comment not found"
        )
    return CommentDetailResponse(
        data=db_comment, success=True, message="Comment retrieved successfully"
    )


@router.put("/{comment_id}", response_model=CommentDetailResponse)
def update_comment(
    comment_id: str, comment: CommentUpdate, db: Session = Depends(get_session)
):
    """Update a comment by ID"""
    db_comment = CommentService.update_comment(
        db=db, comment_id=comment_id, comment=comment
    )
    if not db_comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    return CommentDetailResponse(
        data=db_comment, success=True, message="Comment updated successfully"
    )


@router.delete("/{comment_id}", response_model=CommentDetailResponse)
def delete_comment(comment_id: str, db: Session = Depends(get_session)):
    """Delete a comment by ID"""
    db_comment = CommentService.delete_comment(db=db, comment_id=comment_id)
    if not db_comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    return CommentDetailResponse(
        data=db_comment, success=True, message="Comment deleted successfully"
    )


@router.get("/", response_model=CommentListResponse)
def list_comments(db: Session = Depends(get_session)):
    """List all comments"""
    comments = CommentService.list_comments(db=db)
    return CommentListResponse(
        data=comments, success=True, message="Comments retrieved successfully"
    )
