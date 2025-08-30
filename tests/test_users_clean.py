"""Tests for user endpoints - clean version"""

from uuid import uuid4


class TestUserAPI:
    """Test user CRUD operations"""

    def test_create_user(self, client):
        """Test user creation"""
        user_data = {"username": "newuser", "full_name": "New User"}

        response = client.post("/api/v1/users/", json=user_data)

        assert response.status_code == 201
        data = response.json()

        assert data["success"] == True
        assert data["message"] == "User created successfully"
        assert data["data"]["username"] == "newuser"
        assert data["data"]["full_name"] == "New User"
        assert "id" in data["data"]
        assert "created_at" in data["data"]

    def test_create_user_duplicate_username(self, client, test_user):
        """Test creating user with duplicate username"""
        user_data = {"username": test_user.username, "full_name": "Another User"}

        response = client.post("/api/v1/users/", json=user_data)

        assert response.status_code == 400
        assert "Username already exists" in response.json()["detail"]

    def test_get_user(self, client, test_user):
        """Test getting a user by ID"""
        response = client.get(f"/api/v1/users/{test_user.id}")

        assert response.status_code == 200
        data = response.json()

        assert data["success"] == True
        assert data["message"] == "User retrieve successfully"
        assert data["data"]["id"] == str(test_user.id)
        assert data["data"]["username"] == test_user.username
        assert data["data"]["full_name"] == test_user.full_name

    def test_get_user_not_found(self, client):
        """Test getting non-existent user"""
        fake_id = uuid4()
        response = client.get(f"/api/v1/users/{fake_id}")

        assert response.status_code == 404
        assert "User not found" in response.json()["detail"]

    def test_list_users(self, client, test_user, test_user2):
        """Test listing all users"""
        response = client.get("/api/v1/users/")

        assert response.status_code == 200
        data = response.json()

        assert data["success"] == True
        assert data["message"] == "Users retrieved successfully"
        assert isinstance(data["data"], list)
        assert len(data["data"]) >= 2  # At least our test users

        # Check that our test users are in the list
        usernames = [user["username"] for user in data["data"]]
        assert test_user.username in usernames
        assert test_user2.username in usernames

    def test_update_user(self, client, test_user):
        """Test updating a user"""
        update_data = {"username": "updateduser", "full_name": "Updated User Name"}

        response = client.put(f"/api/v1/users/{test_user.id}", json=update_data)

        assert response.status_code == 200
        data = response.json()

        assert data["username"] == "updateduser"
        assert data["full_name"] == "Updated User Name"
        assert data["id"] == str(test_user.id)

    def test_update_user_not_found(self, client):
        """Test updating non-existent user"""
        fake_id = uuid4()
        update_data = {"username": "someuser", "full_name": "Some User"}

        response = client.put(f"/api/v1/users/{fake_id}", json=update_data)

        assert response.status_code == 404
        assert "User not found" in response.json()["detail"]

    def test_delete_user(self, client, session):
        """Test deleting a user"""
        # Create a user specifically for deletion
        from app.models import User

        user = User(username="todelete", full_name="To Delete")
        session.add(user)
        session.commit()
        session.refresh(user)

        response = client.delete(f"/api/v1/users/{user.id}")

        assert response.status_code == 200
        data = response.json()

        assert data["id"] == str(user.id)
        assert data["username"] == "todelete"

    def test_delete_user_not_found(self, client):
        """Test deleting non-existent user"""
        fake_id = uuid4()
        response = client.delete(f"/api/v1/users/{fake_id}")

        assert response.status_code == 404
        assert "User not found" in response.json()["detail"]
