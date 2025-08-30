"""Tests for post endpoints"""

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
