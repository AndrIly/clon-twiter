from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.users import User
from app.schemas.post import CreateTweetResponse, PostCreate, TweetOut, TweetsResponse
from app.services.post_services import PostService

router = APIRouter(
    prefix="/api/tweets",
    tags=["tweets"],
)


@router.get("", response_model=TweetsResponse)
async def get_tweets(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
    offset: int = 0,
    limit: int = 10,
):
    posts = await PostService.get_all_posts(
        db, current_user.id, skip=offset, limit=limit
    )
    return TweetsResponse.from_orm_posts(posts)


@router.post("", response_model=CreateTweetResponse, status_code=201)
async def create_tweet(
    post: PostCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    created = await PostService.create_post(
        db, post.text, current_user.id, post.tweet_media_ids
    )
    return CreateTweetResponse(result=True, tweet_id=created.id)


@router.get("/{tweet_id}", response_model=TweetOut)
async def get_tweet(tweet_id: int, db: AsyncSession = Depends(get_db)):
    post = await PostService.get_post_by_id(db, tweet_id)
    if not post:
        raise HTTPException(status_code=404, detail="Tweet not found")
    return TweetOut.from_orm_post(post)


@router.delete("/{tweet_id}", status_code=200)
async def delete_tweet(
    tweet_id: int,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    deleted = await PostService.delete_post(db, tweet_id, current_user.id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Tweet not found")
    return {"result": True}
