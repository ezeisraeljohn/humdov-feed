"""FastAPI application entrypoint"""

from fastapi import FastAPI
from app.core.session import get_session
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import select
from app.models import User
from app.core import settings
from contextlib import asynccontextmanager
import uvicorn
from app.api.v1 import user_router, post_router


@asynccontextmanager
async def lifespan(app: FastAPI):

    print("🚀 Application startup")
    yield
    print("🛑 Application shutdown")


app = FastAPI(
    lifespan=lifespan,
    docs_url="/api/v1/docs",
    redoc_url="/api/v1/redoc",
    debug=True,
    title="Humdov Feed API",
    description="Humdov Feed API for managing users, posts, likes, and tags.",
    version="1.0.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_router)
app.include_router(post_router)


@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint."""
    print("Health check endpoint called")
    return {"status": "ok"}


@app.get("/api/v1/db-health")
async def db_health_check():
    """Database health check endpoint."""
    try:
        db = next(get_session())
        db.exec(select(User))
        return {"status": "ok"}
    except Exception as e:
        return {"status": "error", "detail": str(e)}


if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
    )
