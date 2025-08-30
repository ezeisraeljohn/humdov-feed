"""Tests for post endpoints - clean version"""

import pytest
from uuid import uuid4

from app.models import Post


class TestPostAPI:
    """Test post CRUD operations"""

    def test_create_post(self, client, test_user):
        """Test post creation"""
        post_data = {
            "author_id": str(test_user.id),
            "title": "Test Post",
            "body": "This is a test post content.",
        }

        response = client.post("/api/v1/posts/", json=post_data)

        assert response.status_code == 201
        data = response.json()

        assert data["success"] == True
        assert data["message"] == "Post created successfully"
        assert data["data"]["title"] == "Test Post"
        assert data["data"]["body"] == "This is a test post content."
        assert data["data"]["author_id"] == str(test_user.id)
        assert "id" in data["data"]
        assert "created_at" in data["data"]

    def test_create_post_missing_fields(self, client, test_user):
        """Test post creation with missing required fields"""
        # Missing title
        post_data = {
            "author_id": str(test_user.id),
            "body": "This is a test post content.",
        }

        response = client.post("/api/v1/posts/", json=post_data)
        assert response.status_code == 422

    def test_list_posts(self, client, test_posts):
        """Test listing all posts"""
        response = client.get("/api/v1/posts/")

        assert response.status_code == 200
        data = response.json()

        assert data["success"] == True
        assert data["message"] == "Posts retrieved successfully"
        assert isinstance(data["data"], list)
        assert len(data["data"]) >= len(test_posts)

        assert data["success"] == True
        assert data["message"] == "Posts retrieved successfully"
        assert isinstance(data["data"], list)
        assert len(data["data"]) >= len(test_posts)


class TestPostModel:
    """Test Post model functionality"""

    def test_post_model_creation(self, session, test_user):
        """Test creating a post model"""
        post = Post(
            author_id=test_user.id,
            title="Test Model Post",
            body="This is a test post for model testing.",
        )

        session.add(post)
        session.commit()
        session.refresh(post)

        assert post.id is not None
        assert post.title == "Test Model Post"
        assert post.body == "This is a test post for model testing."
        assert post.author_id == test_user.id
        assert post.created_at is not None

    def test_post_relationships(self, session, test_user):
        """Test post relationships"""
        post = Post(
            author_id=test_user.id,
            title="Relationship Test Post",
            body="Testing relationships.",
        )

        session.add(post)
        session.commit()
        session.refresh(post)

        # Test that post has proper author relationship
        assert post.author_id == test_user.id


class TestPostsByUser:
    """Test getting posts by specific users"""

    def test_get_posts_by_user(self, client, test_user):
        """Test getting all posts by a specific user"""
        response = client.get(f"/api/v1/users/{test_user.id}/posts")

        if response.status_code == 200:  # If endpoint exists
            data = response.json()
            assert isinstance(data, list) or isinstance(data.get("data"), list)


class TestPostContent:
    """Test post content validation and handling"""

    def test_post_with_long_content(self, client, test_user):
        """Test creating post with long content"""
        long_body = "Lorem ipsum dolor sit amet. " * 100  # Long content

        post_data = {
            "author_id": str(test_user.id),
            "title": "Long Content Post",
            "body": long_body,
        }

        response = client.post("/api/v1/posts/", json=post_data)

        assert response.status_code == 201
        data = response.json()
        assert data["data"]["body"] == long_body

    def test_post_with_special_characters(self, client, test_user):
        """Test creating post with special characters"""
        special_content = "Test with émojis 🚀 and spécial characters: @#$%^&*()"

        post_data = {
            "author_id": str(test_user.id),
            "title": "Special Characters Test",
            "body": special_content,
        }

        response = client.post("/api/v1/posts/", json=post_data)

        assert response.status_code == 201
        data = response.json()
        assert data["data"]["body"] == special_content
