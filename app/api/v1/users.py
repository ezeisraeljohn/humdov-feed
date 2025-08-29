"""User endpoints: create, read, list users"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List
from app.core.session import get_session
from ...models import (
    User,
    UserCreate,
    UserUpdate,
    UserResponse,
    UserDetailResponse,
    UserListResponse,
)
from app.services import UserService

router = APIRouter(prefix="/api/v1/users", tags=["Users"])


@router.post(
    "/", response_model=UserDetailResponse, status_code=status.HTTP_201_CREATED
)
def create_user(
    user: UserCreate, db: Session = Depends(get_session)
) -> UserDetailResponse:
    """Create a new user"""

    try:
        db_user = UserService.create_user(db, user)
        return UserDetailResponse(
            data=db_user, success=True, message="User created successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{user_id}", response_model=UserDetailResponse)
def get_user(user_id: int, db: Session = Depends(get_session)) -> UserDetailResponse:
    """Get a user by ID"""
    db_user = UserService.get_user_by_id(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserDetailResponse(
        data=db_user, success=True, message="User retrieve successfully"
    )


@router.get("/", response_model=UserListResponse)
def list_users(db: Session = Depends(get_session)) -> UserListResponse:
    """List all users"""
    users = db.exec(select(User)).all()
    response = [UserResponse.model_validate(user) for user in users]
    return UserListResponse(
        data=response, success=True, message="Users retrieved successfully"
    )


@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int, user: UserUpdate, db: Session = Depends(get_session)
) -> UserResponse:
    """Update an existing user"""
    db_user = UserService.update_user(db, user_id, user)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    response = UserResponse.model_validate(db_user)
    return response


@router.delete("/{user_id}", response_model=UserResponse)
def delete_user(user_id: int, db: Session = Depends(get_session)) -> UserResponse:
    """Delete a user by ID"""
    db_user = UserService.delete_user(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    response = UserResponse.model_validate(db_user)
    return response
