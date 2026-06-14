from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..middleware.auth import get_current_user
from ..models.users import User
from ..services.like_services import LikeService

router = APIRouter(prefix="/api/tweets", tags=["likes"])


@router.post("/{tweet_id}/likes")
async def like_tweet(
    tweet_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    like = await LikeService.add_like(db, current_user.id, tweet_id)
    if like:
        return {"result": True}
    else:
        raise HTTPException(status_code=404, detail="Tweet not found")


@router.delete("/{tweet_id}/likes")
async def unlike_tweet(
    tweet_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    like = await LikeService.remove_like(db, current_user.id, tweet_id)
    if not like:
        raise HTTPException(status_code=404, detail="Like not found")
    return {"result": True}
