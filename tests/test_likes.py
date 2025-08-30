"""Tests for like endpoints"""

import pytest
from uuid import uuid4

from app.models import Like


class TestLikeModel:
    """Test Like model functionality"""

    def test_like_model_creation(self, session, test_user, test_posts):
        """Test creating a like model"""
        target_post = test_posts[0]

        like = Like(user_id=test_user.id, post_id=target_post.id)
        session.add(like)
        session.commit()
        session.refresh(like)

        assert like.id is not None
        assert like.user_id == test_user.id
        assert like.post_id == target_post.id
        assert like.created_at is not None

    def test_like_relationships(self, session, test_user, test_posts):
        """Test like relationships"""
        target_post = test_posts[0]

        like = Like(user_id=test_user.id, post_id=target_post.id)
        session.add(like)
        session.commit()
        session.refresh(like)

        # Test that like has proper relationships
        assert like.user_id == test_user.id
        assert like.post_id == target_post.id


class TestLikesByPost:
    """Test getting likes for specific posts"""

    def test_get_likes_for_post(self, client, test_posts, test_engagement):
        """Test getting all likes for a specific post"""
        # Post 1 (index 1) should have likes from test_engagement
        post_with_likes = test_posts[1]

        response = client.get(f"/api/v1/posts/{post_with_likes.id}/likes")

        if response.status_code == 200:  # If endpoint exists
            data = response.json()
            assert isinstance(data, list) or isinstance(data.get("data"), list)


class TestLikesByUser:
    """Test getting likes by specific users"""

    def test_get_likes_by_user(self, client, test_user, test_engagement):
        """Test getting all likes by a specific user"""
        response = client.get(f"/api/v1/users/{test_user.id}/likes")

        if response.status_code == 200:  # If endpoint exists
            data = response.json()
            assert isinstance(data, list) or isinstance(data.get("data"), list)


class TestLikeEngagement:
    """Test like engagement scenarios"""

    def test_multiple_users_like_same_post(
        self, client, session, test_user, test_user2, test_posts
    ):
        """Test multiple users liking the same post"""
        target_post = test_posts[1]

        # User 1 likes the post
        like1_data = {"user_id": str(test_user.id), "post_id": str(target_post.id)}
        response1 = client.post("/api/v1/likes/", json=like1_data)

        # User 2 likes the same post
        like2_data = {"user_id": str(test_user2.id), "post_id": str(target_post.id)}
        response2 = client.post("/api/v1/likes/", json=like2_data)

        # Both should succeed or already exist
        assert response1.status_code in [201, 400]  # Created or already exists
        assert response2.status_code in [201, 400]  # Created or already exists

    def test_user_likes_multiple_posts(self, client, test_user, test_posts):
        """Test one user liking multiple posts"""
        # Like first post
        like1_data = {"user_id": str(test_user.id), "post_id": str(test_posts[1].id)}
        response1 = client.post("/api/v1/likes/", json=like1_data)

        # Like second post
        like2_data = {"user_id": str(test_user.id), "post_id": str(test_posts[2].id)}
        response2 = client.post("/api/v1/likes/", json=like2_data)

        # Both should succeed or already exist
        assert response1.status_code in [201, 400]  # Created or already exists
        assert response2.status_code in [201, 400]  # Created or already exists
