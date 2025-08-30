"""Functions to generate and insert demo data"""

import random
from datetime import datetime, timedelta
from typing import List
from uuid import UUID
from faker import Faker
from sqlmodel import Session, select, delete
from ..models import (
    User,
    UserCreate,
    Post,
    PostCreate,
    Like,
    LikeCreate,
    Comment,
    CommentCreate,
    Tag,
    TagCreate,
    PostTag,
    PostTagCreate,
)

fake = Faker()


class SeedService:
    """Service for seeding the database with demo data"""

    @staticmethod
    def create_users(db: Session, count: int = 20) -> List[User]:
        """Create demo users"""
        users = []
        print(f"Creating {count} users...")

        for i in range(count):
            user_data = UserCreate(
                username=fake.unique.user_name(), full_name=fake.name()
            )
            user = User.model_validate(user_data.model_dump())
            db.add(user)
            users.append(user)

        db.commit()

        # Refresh to get IDs
        for user in users:
            db.refresh(user)

        print(f"Created {len(users)} users")
        return users

    @staticmethod
    def create_tags(db: Session, count: int = 50) -> List[Tag]:
        """Create demo tags"""
        tags = []
        print(f"Creating {count} tags...")

        # Common tag categories for variety
        tag_categories = [
            # Tech tags
            "python",
            "javascript",
            "react",
            "fastapi",
            "database",
            "api",
            "web-development",
            "machine-learning",
            "data-science",
            "backend",
            "frontend",
            "devops",
            "cloud",
            # Lifestyle tags
            "travel",
            "food",
            "photography",
            "fitness",
            "music",
            "art",
            "books",
            "movies",
            "gaming",
            "sports",
            "nature",
            "cooking",
            "health",
            "fashion",
            "design",
            # Business tags
            "startup",
            "entrepreneurship",
            "marketing",
            "finance",
            "business",
            "productivity",
            "leadership",
            "innovation",
            "strategy",
            "networking",
            "career",
            "remote-work",
            # Educational tags
            "tutorial",
            "learning",
            "education",
            "science",
            "technology",
            "programming",
            "tips",
            "guide",
            "howto",
            "best-practices",
        ]

        # Use predefined tags and generate additional ones if needed
        selected_tags = random.sample(tag_categories, min(count, len(tag_categories)))

        # Generate additional random tags if needed
        while len(selected_tags) < count:
            selected_tags.append(fake.word().lower())

        for tag_name in selected_tags[:count]:
            try:
                tag_data = TagCreate(tag=tag_name)
                tag = Tag.model_validate(tag_data.model_dump())
                db.add(tag)
                tags.append(tag)
            except Exception as e:
                # Skip if tag already exists (unique constraint)
                print(f"Skipping duplicate tag: {tag_name}")
                continue

        db.commit()

        # Refresh to get IDs
        for tag in tags:
            db.refresh(tag)

        print(f"Created {len(tags)} tags")
        return tags

    @staticmethod
    def create_posts(
        db: Session, users: List[User], posts_per_user: int = 500
    ) -> List[Post]:
        """Create demo posts for users"""
        posts = []
        print(f"Creating {posts_per_user} posts per user ({len(users)} users)...")

        for user in users:
            user_posts = []
            for i in range(posts_per_user):
                # Create varied post content
                title = fake.sentence(nb_words=random.randint(3, 8)).rstrip(".")
                body = "\n\n".join(
                    [
                        fake.paragraph(nb_sentences=random.randint(2, 5))
                        for _ in range(random.randint(1, 3))
                    ]
                )

                # Random creation time within the last 30 days
                created_at = fake.date_time_between(start_date="-30d", end_date="now")

                post_data = PostCreate(author_id=user.id, title=title, body=body)

                post = Post.model_validate(post_data.model_dump())
                post.created_at = created_at
                post.updated_at = created_at

                db.add(post)
                user_posts.append(post)
                posts.append(post)

            print(f"  Created {len(user_posts)} posts for user {user.username}")

        db.commit()

        # Refresh to get IDs
        for post in posts:
            db.refresh(post)

        print(f"Created {len(posts)} posts total")
        return posts

    @staticmethod
    def assign_tags_to_posts(db: Session, posts: List[Post], tags: List[Tag]) -> None:
        """Randomly assign tags to posts"""
        print("Assigning tags to posts...")

        post_tags_created = 0
        for post in posts:
            # Each post gets 1-5 random tags
            num_tags = random.randint(1, 5)
            selected_tags = random.sample(tags, min(num_tags, len(tags)))

            for tag in selected_tags:
                post_tag_data = PostTagCreate(post_id=post.id, tag_id=tag.id)
                post_tag = PostTag.model_validate(post_tag_data.model_dump())
                db.add(post_tag)
                post_tags_created += 1

        db.commit()
        print(f"Created {post_tags_created} post-tag relationships")

    @staticmethod
    def create_likes(
        db: Session, users: List[User], posts: List[Post], likes_per_user: int = 40
    ) -> None:
        """Create random likes - each user likes random posts (not their own)"""
        print(f"Creating {likes_per_user} likes per user...")

        likes_created = 0
        for user in users:
            # Get posts that are not from this user
            other_user_posts = [post for post in posts if post.author_id != user.id]

            if len(other_user_posts) < likes_per_user:
                selected_posts = other_user_posts
            else:
                selected_posts = random.sample(other_user_posts, likes_per_user)

            for post in selected_posts:
                like_data = LikeCreate(user_id=user.id, post_id=post.id)
                like = Like.model_validate(like_data.model_dump())

                # Random like time between post creation and now
                like_time = fake.date_time_between(
                    start_date=post.created_at, end_date="now"
                )
                like.created_at = like_time
                like.updated_at = like_time

                db.add(like)
                likes_created += 1

        db.commit()
        print(f"Created {likes_created} likes")

    @staticmethod
    def create_comments(
        db: Session, users: List[User], posts: List[Post], comments_per_user: int = 40
    ) -> None:
        """Create random comments - each user comments on random posts (not their own)"""
        print(f"Creating {comments_per_user} comments per user...")

        comments_created = 0
        for user in users:
            # Get posts that are not from this user
            other_user_posts = [post for post in posts if post.author_id != user.id]

            if len(other_user_posts) < comments_per_user:
                selected_posts = other_user_posts
            else:
                selected_posts = random.sample(other_user_posts, comments_per_user)

            for post in selected_posts:
                # Generate comment content
                content = fake.paragraph(nb_sentences=random.randint(1, 3))

                comment_data = CommentCreate(
                    user_id=user.id, post_id=post.id, content=content
                )
                comment = Comment.model_validate(comment_data.model_dump())

                # Random comment time between post creation and now
                comment_time = fake.date_time_between(
                    start_date=post.created_at, end_date="now"
                )
                comment.created_at = comment_time
                comment.updated_at = comment_time

                db.add(comment)
                comments_created += 1

        db.commit()
        print(f"Created {comments_created} comments")

    @staticmethod
    def seed_all(
        db: Session,
        num_users: int = 20,
        posts_per_user: int = 500,
        num_tags: int = 50,
        likes_per_user: int = 40,
        comments_per_user: int = 40,
    ) -> None:
        """Seed the entire database with demo data"""
        print("🌱 Starting database seeding...")
        print("=" * 50)
        print(f"Configuration:")
        print(f"   • Users: {num_users}")
        print(f"   • Posts per user: {posts_per_user}")
        print(f"   • Tags: {num_tags}")
        print(f"   • Likes per user: {likes_per_user}")
        print(f"   • Comments per user: {comments_per_user}")
        print("=" * 50)

        # Create users first
        users = SeedService.create_users(db, count=num_users)

        # Create tags
        tags = SeedService.create_tags(db, count=num_tags)

        # Create posts
        posts = SeedService.create_posts(db, users, posts_per_user=posts_per_user)

        # Assign tags to posts
        SeedService.assign_tags_to_posts(db, posts, tags)

        # Create likes
        SeedService.create_likes(db, users, posts, likes_per_user=likes_per_user)

        # Create comments
        SeedService.create_comments(
            db, users, posts, comments_per_user=comments_per_user
        )

        print("=" * 50)
        print("Database seeding completed successfully!")
        print(f"Summary:")
        print(f"   • Users: {len(users)}")
        print(f"   • Posts: {len(posts)}")
        print(f"   • Tags: {len(tags)}")
        print(f"   • Likes: ~{len(users) * likes_per_user}")
        print(f"   • Comments: ~{len(users) * comments_per_user}")

    @staticmethod
    def clear_all_data(db: Session) -> None:
        """Clear all data from the database (for testing)"""
        print("Clearing all data from database...")

        # Delete in reverse order of dependencies
        db.execute(delete(PostTag))
        db.execute(delete(Comment))
        db.execute(delete(Like))
        db.execute(delete(Post))
        db.execute(delete(Tag))
        db.execute(delete(User))

        db.commit()
        print("All data cleared")
