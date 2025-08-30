# Humdov Feed API

A social media feed API built with FastAPI, featuring intelligent content ranking and personalized feeds based on user engagement and interests.

## Features

- **User Management**: Create, read, update, and delete users
- **Post Management**: Full CRUD operations for posts with rich content
- **Social Interactions**: Like and comment on posts
- **Tag System**: Categorize posts with tags for better content discovery
- **Intelligent Feed Ranking**: Advanced algorithm for personalized content delivery
- **Pagination**: Efficient pagination for all list endpoints
- **Database Seeding**: Comprehensive seeding system with realistic demo data

## Architecture

### Tech Stack

- **Framework**: FastAPI with async support
- **Database**: SQLModel (SQLAlchemy + Pydantic) with PostgreSQL/SQLite support
- **API Documentation**: Auto-generated OpenAPI/Swagger docs
- **Testing**: Pytest with fixtures
- **Data Generation**: Faker for realistic demo data

### Project Structure

```
humdov-feed/
├── app/
│   ├── api/v1/          # API endpoints (users, posts, likes, comments, feed)
│   ├── core/            # Database, settings, and session management
│   ├── models/          # SQLModel definitions and Pydantic schemas
│   └── services/        # Business logic layer
├── scripts/             # Database utilities (seeding, reset)
├── tests/               # Test suite
├── alembic/             # Database migrations
└── requirements.txt     # Python dependencies
```

## Installation & Setup

### Prerequisites

- Python 3.11+
- PostgreSQL (optional, SQLite works for development)

### Environment Setup

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd humdov-feed
   ```

2. **Create virtual environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Configuration**

   ```bash
   cp .env.example .env.development
   # Edit .env.development with your database URL
   ```

5. **Run the application**

   ```bash
   # Using uvicorn directly
   uvicorn app.main:app --reload

   # Or using the Makefile
   make run
   ```

6. **Access the API**
   - API Documentation: http://localhost:8000/api/v1/docs
   - ReDoc Documentation: http://localhost:8000/api/v1/redoc
   - Health Check: http://localhost:8000/api/v1/health

## Database Seeding

The application includes a seeding system to populate your database with realistic demo data for testing and development.

### Seeding Options

#### Interactive Mode (Recommended)

```bash
python scripts/seed.py
```

This launches an interactive prompt where you can customize:

- Number of users (minimum: 10, default: 20)
- Posts per user (minimum: 50, default: 500)
- Number of tags (minimum: 20, default: 50)
- Likes per user (minimum: 40, default: 40)
- Comments per user (minimum: 40, default: 40)

#### Quick Seeding

```bash
python scripts/seed.py --quick
```

Uses default values without prompts - perfect for CI/CD or quick setup.

#### Clear Database

```bash
python scripts/seed.py --clear
```

**Warning**: This will delete ALL existing data!

#### Help

```bash
python scripts/seed.py --help
```

### What Gets Created

The seeding process generates:

- **Realistic Users**: Unique usernames and full names using Faker
- **Diverse Content**: Posts with varied titles and multi-paragraph content
- **Rich Tag System**: 50+ predefined tags across tech, lifestyle, business, and education categories
- **Authentic Engagement**: Users like and comment on posts from other users (never their own)
- **Temporal Distribution**: Posts created over the last 30 days with realistic timestamps
- **Relationship Mapping**: Each post gets 1-5 random tags for content categorization

## Feed Ranking Algorithm

The heart of the application is our feed ranking algorithm that delivers personalized content based on multiple engagement and relevance factors.

### Mathematical Model

The feed score for each post is calculated using this formula:

```
Feed Score = (wₗ × likes) + (wᶜ × comments) + (wₜ × tag_matches) + time_decay
```

Where:

- `wₗ` = Like weight (1.0 point per like)
- `wᶜ` = Comment weight (3.0 points per comment)
- `wₜ` = Tag match weight (2.0 points per matching tag)
- `time_decay` = Freshness factor based on post age

### Algorithm Components

#### 1. Engagement Scoring

- **Likes**: Basic engagement indicator (weight: 1.0)
- **Comments**: High-value engagement showing deeper interest (weight: 3.0)
- Comments are weighted 3x more than likes because they indicate deeper engagement

#### 2. Interest Matching

- **Tag Analysis**: Compares post tags with user's historical interests
- **User Profiling**: Builds interest profile from tags on user's own posts
- **Relevance Boost**: +2 points for each shared tag between post and user interests

#### 3. Time Decay Function

```python
time_decay = 1 / (hours_since_posted + 1)
```

- **Fresh Content Boost**: Recently posted content gets higher scores
- **Gradual Decay**: Older content gradually loses relevance
- **Prevents Staleness**: Ensures feed doesn't get dominated by old viral content

### Real-World Example

**Scenario**: User interested in `python` and `web-development` (based on their post history)

**Post A**:

- 10 likes, 2 comments
- Posted 1 hour ago
- Tags: `python`, `fastapi` (1 match with user interests)

**Post B**:

- 20 likes, 0 comments
- Posted 3 days ago (72 hours)
- Tags: `javascript` (0 matches with user interests)

**Calculations**:

Post A Score:

```
(1.0 × 10) + (3.0 × 2) + (2.0 × 1) + (1/(1+1))
= 10 + 6 + 2 + 0.5 = 18.5
```

Post B Score:

```
(1.0 × 20) + (3.0 × 0) + (2.0 × 0) + (1/(72+1))
= 20 + 0 + 0 + 0.014 ≈ 20.0
```

**Result**: Despite having fewer total engagements, Post A would rank higher due to recency and tag relevance, demonstrating the algorithm's emphasis on personalization and freshness.

### Algorithm Benefits

1. **Personalization**: Content matching user interests gets priority
2. **Quality Over Quantity**: Comments weighted more than likes
3. **Freshness**: Recent content gets algorithmic boost
4. **Engagement-Driven**: Popular content naturally rises
5. **Balanced Scoring**: No single factor dominates the ranking

### Implementation Details

The algorithm is implemented in `app/services/feed_service.py` with the following key methods:

- `get_user_tags()`: Analyzes user's posting history to build interest profile
- `calculate_tag_matches()`: Counts shared tags between post and user interests
- `calculate_time_decay()`: Applies temporal relevance scoring
- `get_post_engagement_stats()`: Aggregates likes and comments
- `calculate_feed_score()`: Combines all factors into final ranking score

## API Endpoints

### Authentication

Currently, the API operates without authentication for development purposes.

### Core Endpoints

#### Users

- `POST /api/v1/users` - Create new user
- `GET /api/v1/users/{user_id}` - Get user by ID
- `GET /api/v1/users` - List all users
- `PUT /api/v1/users/{user_id}` - Update user
- `DELETE /api/v1/users/{user_id}` - Delete user

#### Posts

- `POST /api/v1/posts` - Create new post
- `GET /api/v1/posts/{post_id}` - Get post by ID
- `GET /api/v1/posts` - List all posts

#### Social Interactions

- `POST /api/v1/likes` - Like a post
- `DELETE /api/v1/likes/{like_id}` - Unlike a post
- `GET /api/v1/likes/post/{post_id}` - Get likes for post
- `POST /api/v1/comments` - Comment on post
- `GET /api/v1/comments/{comment_id}` - Get comment
- `PUT /api/v1/comments/{comment_id}` - Update comment
- `DELETE /api/v1/comments/{comment_id}` - Delete comment

#### Tags

- `POST /api/v1/tags` - Create tag
- `GET /api/v1/tags/{tag_id}` - Get tag
- `POST /api/v1/tags/post-tags` - Associate tag with post

#### Personalized Feed

- `GET /api/v1/feeds/{user_id}` - Get personalized feed
  - Query parameters:
    - `page`: Page number (default: 1)
    - `page_size`: Items per page (default: 20, max: 100)

### Response Format

All endpoints return consistent JSON responses:

```json
{
  "data": {},
  "success": true,
  "message": "Operation completed successfully",
  "pagination": {
    // For paginated endpoints
    "page": 1,
    "page_size": 20,
    "total_items": 100,
    "total_pages": 5,
    "has_next": true,
    "has_previous": false
  }
}
```

## Testing

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_feed.py

# Verbose output
pytest -v
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is part of the Humdov technical assessment.

---

**Built with ❤️ using FastAPI, SQLModel, and modern Python practices.**
