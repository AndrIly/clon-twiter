from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.users import User
from app.schemas.user import UserCreate, UserResponse
from app.services.follow_services import FollowServices
from app.services.user_services import UserService

router = APIRouter(prefix="/api/users", tags=["users"])


@router.post("", response_model=UserResponse, status_code=201)
async def register_user(data: UserCreate, db: AsyncSession = Depends(get_db)):
    existing = await UserService.get_user_by_api_key(db, data.api_key)
    if existing:
        raise HTTPException(status_code=409, detail="api_key already exists")
    user = await UserService.create_user(db, data)
    return UserResponse.from_orm_user(user)


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return UserResponse.from_orm_user(current_user)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    user = await UserService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse.from_orm_user(user)


@router.post("/{user_id}/follow", tags=["users"])
async def follow_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    user = await UserService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    result = await FollowServices.add_follow(db, current_user.id, user.id)
    if result:
        return {"result": True}
    return {"result": False}


@router.delete("/{user_id}/follow", tags=["users"])
async def unfollow_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    user = await UserService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    result = await FollowServices.remove_follow(db, current_user.id, user.id)
    return {"result": result}
