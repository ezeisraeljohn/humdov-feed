"""Tests for database seeding functionality"""

import pytest
from sqlmodel import Session, select

from app.services.seed_service import SeedService
from app.models import User, Post, Tag, Like, Comment, PostTag


class TestSeedService:
    """Test the database seeding service"""

    def test_create_users(self, session):
        """Test user creation in seeding"""
        users = SeedService.create_users(session, count=3)

        assert len(users) == 3

        # Check that users were actually saved to database
        db_users = session.exec(select(User)).all()
        assert len(db_users) == 3

        # Check that usernames are unique
        usernames = [user.username for user in users]
        assert len(set(usernames)) == len(usernames)

        # Check that all users have required fields
        for user in users:
            assert user.id is not None
            assert user.username is not None
            assert user.full_name is not None
            assert user.created_at is not None

    def test_create_tags(self, session):
        """Test tag creation in seeding"""
        tags = SeedService.create_tags(session, count=5)

        assert len(tags) <= 5  # Might be less due to duplicates

        # Check that tags were saved to database
        db_tags = session.exec(select(Tag)).all()
        assert len(db_tags) >= 1

        # Check that tag names are unique
        tag_names = [tag.tag for tag in tags]
        assert len(set(tag_names)) == len(tag_names)

    def test_create_posts(self, session):
        """Test post creation in seeding"""
        # First create users
        users = SeedService.create_users(session, count=2)

        # Then create posts
        posts = SeedService.create_posts(session, users, posts_per_user=3)

        assert len(posts) == 6  # 2 users * 3 posts each

        # Check that posts were saved to database
        db_posts = session.exec(select(Post)).all()
        assert len(db_posts) == 6

        # Check that posts have required fields
        for post in posts:
            assert post.id is not None
            assert post.title is not None
            assert post.body is not None
            assert post.author_id is not None
            assert post.created_at is not None

        # Check that posts are distributed among users
        user_post_counts = {}
        for post in posts:
            user_post_counts[post.author_id] = (
                user_post_counts.get(post.author_id, 0) + 1
            )

        assert len(user_post_counts) == 2  # Both users should have posts
        for count in user_post_counts.values():
            assert count == 3  # Each user should have 3 posts

    def test_assign_tags_to_posts(self, session):
        """Test tag assignment to posts"""
        # Create prerequisite data
        users = SeedService.create_users(session, count=1)
        tags = SeedService.create_tags(session, count=5)
        posts = SeedService.create_posts(session, users, posts_per_user=2)

        # Assign tags to posts
        SeedService.assign_tags_to_posts(session, posts, tags)

        # Check that post-tag relationships were created
        post_tags = session.exec(select(PostTag)).all()
        assert len(post_tags) > 0

        # Check that each post has at least one tag
        post_ids_with_tags = set(pt.post_id for pt in post_tags)
        assert len(post_ids_with_tags) == len(posts)

    def test_create_likes(self, session):
        """Test like creation in seeding"""
        # Create prerequisite data
        users = SeedService.create_users(session, count=2)
        posts = SeedService.create_posts(session, users, posts_per_user=2)

        # Create likes
        SeedService.create_likes(session, users, posts, likes_per_user=2)

        # Check that likes were created
        likes = session.exec(select(Like)).all()
        assert len(likes) > 0

        # Check that users don't like their own posts
        for like in likes:
            post = session.get(Post, like.post_id)
            assert like.user_id != post.author_id

    def test_create_comments(self, session):
        """Test comment creation in seeding"""
        # Create prerequisite data
        users = SeedService.create_users(session, count=2)
        posts = SeedService.create_posts(session, users, posts_per_user=2)

        # Create comments
        SeedService.create_comments(session, users, posts, comments_per_user=2)

        # Check that comments were created
        comments = session.exec(select(Comment)).all()
        assert len(comments) > 0

        # Check that users don't comment on their own posts
        for comment in comments:
            post = session.get(Post, comment.post_id)
            assert comment.user_id != post.author_id

        # Check that comments have content
        for comment in comments:
            assert comment.content is not None
            assert len(comment.content) > 0

    def test_seed_all_integration(self, session):
        """Test the complete seeding process"""
        # Run the full seeding process with small numbers
        SeedService.seed_all(
            session,
            num_users=3,
            posts_per_user=5,
            num_tags=10,
            likes_per_user=3,
            comments_per_user=2,
        )

        # Check that all data was created
        users = session.exec(select(User)).all()
        posts = session.exec(select(Post)).all()
        tags = session.exec(select(Tag)).all()
        likes = session.exec(select(Like)).all()
        comments = session.exec(select(Comment)).all()
        post_tags = session.exec(select(PostTag)).all()

        assert len(users) == 3
        assert len(posts) == 15  # 3 users * 5 posts
        assert len(tags) <= 10  # Might be less due to duplicates
        assert len(likes) > 0
        assert len(comments) > 0
        assert len(post_tags) > 0

        # Check data integrity
        # All posts should have authors
        for post in posts:
            assert post.author_id in [user.id for user in users]

        # All likes should reference valid users and posts
        for like in likes:
            assert like.user_id in [user.id for user in users]
            assert like.post_id in [post.id for post in posts]

        # All comments should reference valid users and posts
        for comment in comments:
            assert comment.user_id in [user.id for user in users]
            assert comment.post_id in [post.id for post in posts]

    def test_clear_all_data(self, session):
        """Test clearing all seeded data"""
        # First seed some data
        SeedService.seed_all(
            session,
            num_users=2,
            posts_per_user=2,
            num_tags=3,
            likes_per_user=1,
            comments_per_user=1,
        )

        # Verify data exists
        assert len(session.exec(select(User)).all()) > 0
        assert len(session.exec(select(Post)).all()) > 0

        # Clear all data
        SeedService.clear_all_data(session)

        # Verify all data is gone
        assert len(session.exec(select(User)).all()) == 0
        assert len(session.exec(select(Post)).all()) == 0
        assert len(session.exec(select(Tag)).all()) == 0
        assert len(session.exec(select(Like)).all()) == 0
        assert len(session.exec(select(Comment)).all()) == 0
        assert len(session.exec(select(PostTag)).all()) == 0


class TestSeedDataQuality:
    """Test the quality and realism of seeded data"""

    def test_user_data_quality(self, session):
        """Test that created users have realistic data"""
        users = SeedService.create_users(session, count=5)

        for user in users:
            # Username should not be empty
            assert len(user.username) > 0

            # Full name should look realistic (contain space for first/last name)
            assert user.full_name is not None and len(user.full_name) > 0

            # Usernames should be unique
            other_users = [u for u in users if u.id != user.id]
            other_usernames = [u.username for u in other_users]
            assert user.username not in other_usernames

    def test_tag_diversity(self, session):
        """Test that tags are diverse and realistic"""
        tags = SeedService.create_tags(session, count=20)

        # Should have variety of tags
        tag_names = [tag.tag for tag in tags]

        # Check for some expected categories
        tech_tags = ["python", "javascript", "fastapi", "database", "api"]
        lifestyle_tags = ["travel", "food", "photography", "fitness"]

        # At least some tags should be from predefined categories
        found_tech = any(tag for tag in tag_names if tag in tech_tags)
        found_lifestyle = any(tag for tag in tag_names if tag in lifestyle_tags)

        assert found_tech or found_lifestyle  # Should have at least one category

    def test_engagement_realism(self, session):
        """Test that likes and comments follow realistic patterns"""
        # Create test data
        users = SeedService.create_users(session, count=3)
        posts = SeedService.create_posts(session, users, posts_per_user=2)
        SeedService.create_likes(session, users, posts, likes_per_user=2)
        SeedService.create_comments(session, users, posts, comments_per_user=1)

        likes = session.exec(select(Like)).all()
        comments = session.exec(select(Comment)).all()

        # Users should not like or comment on their own posts
        for like in likes:
            post = session.get(Post, like.post_id)
            assert (
                like.user_id != post.author_id
            ), "Users should not like their own posts"

        for comment in comments:
            post = session.get(Post, comment.post_id)
            assert (
                comment.user_id != post.author_id
            ), "Users should not comment on their own posts"

        # Comments should have realistic content
        for comment in comments:
            assert (
                len(comment.content) >= 10
            ), "Comments should have substantial content"
