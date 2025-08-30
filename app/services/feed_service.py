"""Business logic for personalized feed ranking"""

from datetime import datetime
from sqlmodel import Session, select, func
from typing import List, Dict, Any
from uuid import UUID
from ..models import Post, User, Like, Comment, PostTag, Tag


class FeedService:
    """Service class for personalized feed operations"""

    # Feed ranking weights
    LIKE_WEIGHT = 1.0
    COMMENT_WEIGHT = 3.0
    TAG_MATCH_WEIGHT = 2.0

    @staticmethod
    def calculate_time_decay(post_created_at: datetime) -> float:
        """Calculate time decay factor based on post age"""
        now = datetime.now()
        hours_since_posted = (now - post_created_at).total_seconds() / 3600
        return 1 / (hours_since_posted + 1)

    @staticmethod
    def get_user_tags(db: Session, user_id: UUID) -> List[UUID]:
        """Get all tags associated with a user's posts"""
        statement = select(PostTag.tag_id).join(Post).where(Post.author_id == user_id)
        results = db.exec(statement)
        return [tag_id for tag_id in results]

    @staticmethod
    def calculate_tag_matches(db: Session, post_id: UUID, user_tags: List[UUID]) -> int:
        """Calculate how many tags a post shares with the user's interests"""
        statement = select(PostTag.tag_id).where(PostTag.post_id == post_id)
        post_tags = db.exec(statement).all()
        return len(set(post_tags) & set(user_tags))

    @staticmethod
    def get_post_engagement_stats(db: Session, post_id: UUID) -> Dict[str, int]:
        """Get likes and comments count for a post"""
        # Count likes
        likes_count = (
            db.exec(
                select(func.count()).select_from(Like).where(Like.post_id == post_id)
            ).first()
            or 0
        )

        # Count comments
        comments_count = (
            db.exec(
                select(func.count())
                .select_from(Comment)
                .where(Comment.post_id == post_id)
            ).first()
            or 0
        )

        return {"likes": likes_count, "comments": comments_count}

    @staticmethod
    def calculate_feed_score(
        likes: int, comments: int, tag_matches: int, time_decay: float
    ) -> float:
        """Calculate the feed score using the ranking formula"""
        score = (
            (FeedService.LIKE_WEIGHT * likes)
            + (FeedService.COMMENT_WEIGHT * comments)
            + (FeedService.TAG_MATCH_WEIGHT * tag_matches)
            + time_decay
        )
        return score

    @staticmethod
    def get_personalized_feed(
        db: Session, user_id: UUID, page: int = 1, page_size: int = 50
    ) -> Dict[str, Any]:
        """Get personalized feed for a user with ranking scores and pagination"""
        # Verify user exists
        user = db.get(User, user_id)
        if not user:
            return {
                "items": [],
                "pagination": {
                    "page": page,
                    "page_size": page_size,
                    "total_items": 0,
                    "total_pages": 0,
                    "has_next": False,
                    "has_previous": False,
                },
            }

        # Get user's tags (interests based on their posts)
        user_tags = FeedService.get_user_tags(db, user_id)

        # Get all posts (excluding user's own posts for now)
        statement = select(Post).where(Post.author_id != user_id)
        posts = db.exec(statement).all()

        feed_items = []

        for post in posts:
            # Get engagement stats
            engagement = FeedService.get_post_engagement_stats(db, post.id)

            # Calculate tag matches
            tag_matches = FeedService.calculate_tag_matches(db, post.id, user_tags)

            # Calculate time decay
            time_decay = FeedService.calculate_time_decay(post.created_at)

            # Calculate final feed score
            score = FeedService.calculate_feed_score(
                engagement["likes"], engagement["comments"], tag_matches, time_decay
            )

            feed_items.append(
                {
                    "post": post,
                    "score": score,
                    "likes_count": engagement["likes"],
                    "comments_count": engagement["comments"],
                    "tag_matches": tag_matches,
                    "time_decay": time_decay,
                }
            )

        # Sort by score (highest first)
        feed_items.sort(key=lambda x: x["score"], reverse=True)

        # Calculate pagination
        total_items = len(feed_items)
        total_pages = (total_items + page_size - 1) // page_size  # Ceiling division

        # Calculate offset
        offset = (page - 1) * page_size

        # Slice the results for pagination
        paginated_items = feed_items[offset : offset + page_size]

        return {
            "items": paginated_items,
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total_items": total_items,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_previous": page > 1,
            },
        }
