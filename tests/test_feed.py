"""Tests for feed endpoint and feed service functionality"""

import pytest
from datetime import datetime, timedelta
from uuid import uuid4

from app.services.feed_service import FeedService
from app.models import User, Post, Tag, Like, Comment, PostTag


class TestFeedService:
    """Test the feed ranking algorithm and service methods"""

    def test_calculate_time_decay(self):
        """Test time decay calculation"""
        # Test recent post (1 hour ago)
        recent_time = datetime.now() - timedelta(hours=1)
        recent_decay = FeedService.calculate_time_decay(recent_time)

        # Test old post (24 hours ago)
        old_time = datetime.now() - timedelta(hours=24)
        old_decay = FeedService.calculate_time_decay(old_time)

        # Recent posts should have higher decay value
        assert recent_decay > old_decay
        assert recent_decay == pytest.approx(0.5, rel=0.1)  # 1/(1+1)
        assert old_decay == pytest.approx(0.04, rel=0.1)  # 1/(24+1)

    def test_calculate_feed_score(self):
        """Test feed score calculation formula"""
        # Test case from the example in requirements
        # Post A: 10 likes, 2 comments, 2 tag matches, 1 hour old
        score_a = FeedService.calculate_feed_score(
            likes=10, comments=2, tag_matches=2, time_decay=0.5  # 1/(1+1)
        )

        # Expected: (1*10) + (3*2) + (2*2) + 0.5 = 10 + 6 + 4 + 0.5 = 20.5
        assert score_a == pytest.approx(20.5, rel=0.01)

        # Post B: 20 likes, 0 comments, 1 tag match, 72 hours old
        score_b = FeedService.calculate_feed_score(
            likes=20, comments=0, tag_matches=1, time_decay=1 / 73  # 1/(72+1)
        )

        # Expected: (1*20) + (3*0) + (2*1) + 0.014 = 20 + 0 + 2 + 0.014 = 22.014
        assert score_b == pytest.approx(22.014, rel=0.01)

    def test_get_user_tags(self, session, test_user, test_tags):
        """Test user tag extraction from their posts"""
        # Create a post for the user with tags
        post = Post(author_id=test_user.id, title="Test Post", body="Test content")
        session.add(post)
        session.commit()
        session.refresh(post)

        # Add tags to the post
        post_tag1 = PostTag(post_id=post.id, tag_id=test_tags[0].id)
        post_tag2 = PostTag(post_id=post.id, tag_id=test_tags[1].id)
        session.add_all([post_tag1, post_tag2])
        session.commit()

        # Get user tags
        user_tags = FeedService.get_user_tags(session, test_user.id)

        assert len(user_tags) == 2
        assert test_tags[0].id in user_tags
        assert test_tags[1].id in user_tags

    def test_calculate_tag_matches(self, session, test_posts, test_tags):
        """Test tag matching calculation"""
        # Post 1 has python and fastapi tags (indices 0, 1)
        user_tags = [test_tags[0].id, test_tags[2].id]  # python, web-development

        matches = FeedService.calculate_tag_matches(
            session, test_posts[0].id, user_tags
        )

        # Should match on python tag (1 match)
        assert matches == 1

    def test_get_post_engagement_stats(self, session, test_posts, test_engagement):
        """Test post engagement statistics"""
        # Post 2 has 2 likes and 2 comments from test_engagement fixture
        stats = FeedService.get_post_engagement_stats(session, test_posts[1].id)

        assert stats["likes"] == 2  # User 1 and User 2 liked it
        assert stats["comments"] == 2  # User 1 made 2 comments

    def test_get_personalized_feed_empty_user(self, session):
        """Test feed for non-existent user"""
        fake_user_id = uuid4()
        result = FeedService.get_personalized_feed(
            session, fake_user_id, page=1, page_size=10
        )

        assert result["items"] == []
        assert result["pagination"]["total_items"] == 0

    def test_get_personalized_feed_with_data(
        self, session, test_user, test_posts, test_engagement
    ):
        """Test personalized feed generation with real data"""
        # Get feed for test_user (who has engagement with test_posts)
        result = FeedService.get_personalized_feed(
            session, test_user.id, page=1, page_size=10
        )

        # Should return posts from other users (not test_user's own post)
        items = result["items"]
        assert len(items) >= 1  # At least user2's posts

        # Check that scores are calculated
        for item in items:
            assert "score" in item
            assert "likes_count" in item
            assert "comments_count" in item
            assert "tag_matches" in item
            assert "time_decay" in item
            assert item["score"] > 0  # Should have some score

        # Items should be sorted by score (highest first)
        if len(items) > 1:
            for i in range(len(items) - 1):
                assert items[i]["score"] >= items[i + 1]["score"]

    def test_feed_pagination(self, session, test_user, test_posts):
        """Test feed pagination functionality"""
        # Test first page
        page1 = FeedService.get_personalized_feed(
            session, test_user.id, page=1, page_size=1
        )

        assert page1["pagination"]["page"] == 1
        assert page1["pagination"]["page_size"] == 1
        assert len(page1["items"]) <= 1

        # Test page bounds
        if page1["pagination"]["total_items"] > 1:
            assert page1["pagination"]["has_next"] == True

        assert page1["pagination"]["has_previous"] == False


class TestFeedAPI:
    """Test the feed API endpoint"""

    def test_get_feed_success(self, client, test_user, test_posts, test_engagement):
        """Test successful feed retrieval"""
        response = client.get(f"/api/v1/feeds/{test_user.id}")

        assert response.status_code == 200
        data = response.json()

        assert data["success"] == True
        assert "data" in data
        assert "pagination" in data
        assert isinstance(data["data"], list)

    def test_get_feed_with_pagination(self, client, test_user, test_posts):
        """Test feed with pagination parameters"""
        response = client.get(f"/api/v1/feeds/{test_user.id}?page=1&page_size=5")

        assert response.status_code == 200
        data = response.json()

        assert data["pagination"]["page"] == 1
        assert data["pagination"]["page_size"] == 5

    def test_get_feed_user_not_found(self, client):
        """Test feed for non-existent user"""
        fake_user_id = uuid4()
        response = client.get(f"/api/v1/feeds/{fake_user_id}")

        assert response.status_code == 404
        assert "User not found" in response.json()["detail"]

    def test_get_feed_invalid_pagination(self, client, test_user):
        """Test feed with invalid pagination parameters"""
        # Page 0 should be invalid
        response = client.get(f"/api/v1/feeds/{test_user.id}?page=0")
        assert response.status_code == 422

        # Page size too large should be invalid
        response = client.get(f"/api/v1/feeds/{test_user.id}?page_size=200")
        assert response.status_code == 422

    def test_feed_response_structure(
        self, client, test_user, test_posts, test_engagement
    ):
        """Test that feed response has correct structure"""
        response = client.get(f"/api/v1/feeds/{test_user.id}")

        assert response.status_code == 200
        data = response.json()

        # Check top-level structure
        assert "data" in data
        assert "pagination" in data
        assert "success" in data
        assert "message" in data

        # Check pagination structure
        pagination = data["pagination"]
        required_pagination_fields = [
            "page",
            "page_size",
            "total_items",
            "total_pages",
            "has_next",
            "has_previous",
        ]
        for field in required_pagination_fields:
            assert field in pagination

        # Check feed item structure if items exist
        if data["data"]:
            item = data["data"][0]
            required_item_fields = [
                "post",
                "score",
                "likes_count",
                "comments_count",
                "tag_matches",
                "time_decay",
            ]
            for field in required_item_fields:
                assert field in item

            # Check post structure
            post = item["post"]
            required_post_fields = [
                "id",
                "title",
                "body",
                "author_id",
                "created_at",
                "updated_at",
            ]
            for field in required_post_fields:
                assert field in post


class TestFeedRankingLogic:
    """Test the specific ranking logic scenarios"""

    def test_comment_weight_higher_than_likes(
        self, session, test_user, test_user2, test_tags
    ):
        """Test that comments are weighted higher than likes"""
        # Create two similar posts
        post_with_likes = Post(
            author_id=test_user2.id,
            title="Post with many likes",
            body="Content",
            created_at=datetime.now() - timedelta(hours=1),
        )

        post_with_comments = Post(
            author_id=test_user2.id,
            title="Post with comments",
            body="Content",
            created_at=datetime.now() - timedelta(hours=1),
        )

        session.add_all([post_with_likes, post_with_comments])
        session.commit()
        session.refresh(post_with_likes)
        session.refresh(post_with_comments)

        # Add 5 likes to first post
        for i in range(5):
            like = Like(user_id=test_user.id, post_id=post_with_likes.id)
            session.add(like)

        # Add 1 comment to second post
        comment = Comment(
            user_id=test_user.id, post_id=post_with_comments.id, content="Great post!"
        )
        session.add(comment)
        session.commit()

        # Calculate scores
        likes_stats = FeedService.get_post_engagement_stats(session, post_with_likes.id)
        comments_stats = FeedService.get_post_engagement_stats(
            session, post_with_comments.id
        )

        time_decay = FeedService.calculate_time_decay(
            datetime.now() - timedelta(hours=1)
        )

        likes_score = FeedService.calculate_feed_score(
            likes=likes_stats["likes"],
            comments=likes_stats["comments"],
            tag_matches=0,
            time_decay=time_decay,
        )

        comments_score = FeedService.calculate_feed_score(
            likes=comments_stats["likes"],
            comments=comments_stats["comments"],
            tag_matches=0,
            time_decay=time_decay,
        )

        # 1 comment (3 points) should be less than 5 likes (5 points)
        # But this tests our weighting is working
        assert likes_score > comments_score  # 5 likes > 1 comment

        # But 2 comments should beat 5 likes
        comment2 = Comment(
            user_id=test_user.id,
            post_id=post_with_comments.id,
            content="Amazing insights!",
        )
        session.add(comment2)
        session.commit()

        comments_stats_updated = FeedService.get_post_engagement_stats(
            session, post_with_comments.id
        )
        comments_score_updated = FeedService.calculate_feed_score(
            likes=comments_stats_updated["likes"],
            comments=comments_stats_updated["comments"],
            tag_matches=0,
            time_decay=time_decay,
        )

        # 2 comments (6 points) should beat 5 likes (5 points)
        assert comments_score_updated > likes_score

    def test_tag_matching_boost(self, session, test_user, test_user2, test_tags):
        """Test that tag matching provides score boost"""
        # Create user posts to establish interests
        user_post = Post(
            author_id=test_user.id, title="My Python Post", body="I love Python"
        )
        session.add(user_post)
        session.commit()
        session.refresh(user_post)

        # Add python tag to user's post (establishing interest)
        user_post_tag = PostTag(post_id=user_post.id, tag_id=test_tags[0].id)  # python
        session.add(user_post_tag)

        # Create two posts by other user
        matching_post = Post(
            author_id=test_user2.id, title="Python Tutorial", body="Learn Python"
        )

        non_matching_post = Post(
            author_id=test_user2.id, title="Java Tutorial", body="Learn Java"
        )

        session.add_all([matching_post, non_matching_post])
        session.commit()
        session.refresh(matching_post)
        session.refresh(non_matching_post)

        # Add python tag to matching post
        matching_post_tag = PostTag(
            post_id=matching_post.id, tag_id=test_tags[0].id
        )  # python
        session.add(matching_post_tag)
        session.commit()

        # Get user tags and calculate matches
        user_tags = FeedService.get_user_tags(session, test_user.id)

        matching_tag_count = FeedService.calculate_tag_matches(
            session, matching_post.id, user_tags
        )
        non_matching_tag_count = FeedService.calculate_tag_matches(
            session, non_matching_post.id, user_tags
        )

        assert matching_tag_count > non_matching_tag_count
        assert matching_tag_count == 1  # One shared tag (python)
        assert non_matching_tag_count == 0  # No shared tags
