"""Feed endpoint: personalized feed for a user"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session
from typing import Optional
from uuid import UUID
from app.core.session import get_session
from ...models import FeedResponse, FeedItemResponse, PostResponse, PaginationInfo
from app.services import UserService
from app.services.feed_service import FeedService

router = APIRouter(prefix="/api/v1/feeds", tags=["Feed"])


@router.get("/{user_id}", response_model=FeedResponse)
def get_personalized_feed(
    user_id: UUID,
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_session),
) -> FeedResponse:
    """Get personalized feed for a user based on engagement and interests"""

    # Verify user exists
    user = UserService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    try:
        # Get personalized feed items with pagination
        feed_result = FeedService.get_personalized_feed(db, user_id, page, page_size)

        # Convert to response format
        feed_response_items = []
        for item in feed_result["items"]:
            post_response = PostResponse.model_validate(item["post"])
            feed_item = FeedItemResponse(
                post=post_response,
                score=item["score"],
                likes_count=item["likes_count"],
                comments_count=item["comments_count"],
                tag_matches=item["tag_matches"],
                time_decay=item["time_decay"],
            )
            feed_response_items.append(feed_item)

        # Create pagination info
        pagination_info = PaginationInfo(**feed_result["pagination"])

        return FeedResponse(
            data=feed_response_items,
            pagination=pagination_info,
            success=True,
            message=f"Personalized feed retrieved successfully for user {user.username}",
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to retrieve personalized feed: {str(e)}"
        )
