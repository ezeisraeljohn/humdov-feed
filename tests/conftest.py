"""Pytest fixtures for DB setup and test client"""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine, select
from sqlmodel.pool import StaticPool
from datetime import datetime, timedelta

from app.main import app
from app.core.session import get_session
from app.models import User, Post, Tag, Like, Comment, PostTag
from app.services.seed_service import SeedService


@pytest.fixture(name="session")
def session_fixture():
    """Create a test database session"""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    """Create a test client with database session override"""

    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture(name="test_user")
def test_user_fixture(session: Session):
    """Create a test user"""
    user = User(username="testuser", full_name="Test User")
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture(name="test_user2")
def test_user2_fixture(session: Session):
    """Create a second test user"""
    user = User(username="testuser2", full_name="Test User 2")
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture(name="test_tags")
def test_tags_fixture(session: Session):
    """Create test tags"""
    tags = []
    tag_names = [
        "python",
        "fastapi",
        "web-development",
        "machine-learning",
        "data-science",
    ]

    for tag_name in tag_names:
        tag = Tag(tag=tag_name)
        session.add(tag)
        tags.append(tag)

    session.commit()
    for tag in tags:
        session.refresh(tag)

    return tags


@pytest.fixture(name="test_posts")
def test_posts_fixture(
    session: Session, test_user: User, test_user2: User, test_tags: list[Tag]
):
    """Create test posts with tags"""
    posts = []

    # Create posts for user 1
    post1 = Post(
        author_id=test_user.id,
        title="Python FastAPI Tutorial",
        body="Learn how to build APIs with FastAPI",
        created_at=datetime.now() - timedelta(hours=1),
    )
    session.add(post1)
    posts.append(post1)

    # Create posts for user 2
    post2 = Post(
        author_id=test_user2.id,
        title="Machine Learning Basics",
        body="Introduction to machine learning concepts",
        created_at=datetime.now() - timedelta(hours=24),
    )
    session.add(post2)
    posts.append(post2)

    post3 = Post(
        author_id=test_user2.id,
        title="Data Science Project",
        body="Building a data science project from scratch",
        created_at=datetime.now() - timedelta(hours=72),
    )
    session.add(post3)
    posts.append(post3)

    session.commit()
    for post in posts:
        session.refresh(post)

    # Add tags to posts
    # Post 1: python, fastapi tags
    post_tag1 = PostTag(post_id=post1.id, tag_id=test_tags[0].id)  # python
    post_tag2 = PostTag(post_id=post1.id, tag_id=test_tags[1].id)  # fastapi

    # Post 2: machine-learning tag
    post_tag3 = PostTag(post_id=post2.id, tag_id=test_tags[3].id)  # machine-learning

    # Post 3: data-science tag
    post_tag4 = PostTag(post_id=post3.id, tag_id=test_tags[4].id)  # data-science

    session.add_all([post_tag1, post_tag2, post_tag3, post_tag4])
    session.commit()

    return posts


@pytest.fixture(name="test_engagement")
def test_engagement_fixture(
    session: Session, test_user: User, test_user2: User, test_posts: list[Post]
):
    """Create test likes and comments"""
    # User 1 likes and comments on User 2's posts

    # Likes
    like1 = Like(user_id=test_user.id, post_id=test_posts[1].id)  # Like post 2
    like2 = Like(user_id=test_user.id, post_id=test_posts[2].id)  # Like post 3

    # More likes for post 2 to test engagement scoring
    like3 = Like(user_id=test_user2.id, post_id=test_posts[1].id)

    session.add_all([like1, like2, like3])

    # Comments
    comment1 = Comment(
        user_id=test_user.id,
        post_id=test_posts[1].id,
        content="Great explanation of ML!",
    )
    comment2 = Comment(
        user_id=test_user.id,
        post_id=test_posts[1].id,
        content="Looking forward to more content like this",
    )

    session.add_all([comment1, comment2])
    session.commit()

    return {"likes": [like1, like2, like3], "comments": [comment1, comment2]}


@pytest.fixture(name="seeded_data")
def seeded_data_fixture(session: Session):
    """Create seeded data for comprehensive testing"""
    # Create a small dataset using the seeding service
    SeedService.seed_all(
        db=session,
        num_users=5,
        posts_per_user=10,
        num_tags=10,
        likes_per_user=5,
        comments_per_user=3,
    )

    # Return the created data for test use
    users = session.exec(select(User)).all()
    posts = session.exec(select(Post)).all()
    tags = session.exec(select(Tag)).all()

    return {"users": users, "posts": posts, "tags": tags}
