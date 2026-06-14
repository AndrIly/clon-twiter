from fastapi import Depends, Header, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.users import User
from app.services.user_services import UserService


async def get_current_user(
    api_key: str = Header(None, alias="api-key"), db: AsyncSession = Depends(get_db)
) -> User:
    if not api_key:
        raise HTTPException(status_code=401, detail="Missing API key")

    user = await UserService.get_user_by_api_key(db, api_key)
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="Invalid or inactive API key")
    return user
