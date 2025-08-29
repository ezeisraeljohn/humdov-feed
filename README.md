# Humdov Interview Test Backend

## Setup
```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Seeding
```bash
python scripts/seed.py
```

## Testing
```bash
pytest
```

## Endpoints
- POST /users
- GET /users/{id}
- POST /posts
- GET /posts/{id}
- POST /posts/{id}/like
- GET /feed?user_id={id}

## Recommendation Method
Explain briefly here how ranking is done (likes → tags → popularity → recency).
