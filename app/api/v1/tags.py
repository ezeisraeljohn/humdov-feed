"""Create Tag endpoints: create, read, update, delete tags"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from ...models import (
    Tag,
    TagCreate,
    TagUpdate,
    TagResponse,
    TagDetailResponse,
    TagListResponse,
    PostTag,
    PostTagCreate,
    PostTagResponse,
    PostTagDetailResponse,
)

from ...core.session import get_session
from ...services import TagService


router = APIRouter(prefix="/api/v1/tags", tags=["Tags"])


@router.post("/", response_model=TagDetailResponse, status_code=status.HTTP_201_CREATED)
def create_tag(tag: TagCreate, db: Session = Depends(get_session)):
    """Create a new tag"""
    try:
        db_tag = TagService.create_tag(db=db, tag=tag)
        return TagDetailResponse(
            data=db_tag, success=True, message="Tag created successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{tag_id}", response_model=TagDetailResponse)
def get_tag(tag_id: int, db: Session = Depends(get_session)):
    """Get a tag by ID"""
    db_tag = TagService.get_tag_by_id(db=db, tag_id=tag_id)
    if not db_tag:
        return TagDetailResponse(data=None, success=False, message="Tag not found")
    return TagDetailResponse(
        data=db_tag, success=True, message="Tag retrieved successfully"
    )


@router.put("/{tag_id}", response_model=TagDetailResponse)
def update_tag(tag_id: int, tag: TagUpdate, db: Session = Depends(get_session)):
    """Update a tag by ID"""
    db_tag = TagService.update_tag(db=db, tag_id=tag_id, tag=tag)
    if not db_tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    return


@router.post(
    "/post-tags",
    response_model=PostTagDetailResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_post_tag(post_tag: PostTagCreate, db: Session = Depends(get_session)):
    """Create a new post-tag relationship"""
    try:
        db_post_tag = TagService.create_post_tag(db=db, post_tag=post_tag)
        return PostTagDetailResponse(
            data=db_post_tag,
            success=True,
            message="Post-Tag relationship created successfully",
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
