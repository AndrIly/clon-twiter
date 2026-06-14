from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Follow
from app.models.users import User
from app.schemas.user import UserCreate

_USER_LOADERS = (
    selectinload(User.following).selectinload(Follow.following),
    selectinload(User.followers).selectinload(Follow.follower),
)


class UserService:
    @staticmethod
    async def create_user(db: AsyncSession, user_data: UserCreate) -> User:
        user = User(**user_data.model_dump())
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

    @staticmethod
    async def get_user_by_api_key(db: AsyncSession, api_key: str) -> User | None:
        result = await db.execute(
            select(User).options(*_USER_LOADERS).where(User.api_key == api_key)
        )
        user = result.scalar_one_or_none()
        return user

    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: int) -> User | None:
        result = await db.execute(
            select(User).options(*_USER_LOADERS).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        return user
