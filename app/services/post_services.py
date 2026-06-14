from typing import List

from sqlalchemy import and_, delete, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Media
from app.models.follow import Follow
from app.models.like import Like
from app.models.post import Post

_POST_LOADERS = (
    selectinload(Post.author),
    selectinload(Post.likes).selectinload(Like.user),
    selectinload(Post.media),
)


class PostService:
    @staticmethod
    async def create_post(
        db: AsyncSession, content: str, user_id: int, media: List[int] | None = None
    ) -> Post:
        post = Post(
            content=content,
            user_id=user_id,
            likes_count=0,
        )
        db.add(post)
        await db.commit()

        if media:
            await db.execute(
                update(Media).where(Media.id.in_(media)).values(tweet_id=post.id)
            )
            await db.commit()
        created = await PostService.get_post_by_id(db, post.id)
        assert created is not None
        return created

    @staticmethod
    async def get_all_posts(
        db: AsyncSession, user_id, skip: int = 0, limit: int = 10
    ) -> List[Post]:
        follow = select(Follow.following_id).where(Follow.follower_id == user_id)
        result = await db.execute(
            select(Post)
            .options(*_POST_LOADERS)
            .where(or_(Post.user_id.in_(follow), Post.user_id == user_id))
            .order_by(Post.likes_count.desc())
            .offset(skip)
            .limit(limit)
        )
        post = result.scalars().all()
        return list(post)

    @staticmethod
    async def get_post_by_id(db: AsyncSession, post_id: int) -> Post | None:
        result = await db.execute(
            select(Post).options(*_POST_LOADERS).where(Post.id == post_id)
        )
        post = result.scalar_one_or_none()
        return post

    @staticmethod
    async def delete_post(db: AsyncSession, post_id: int, user_id: int) -> bool:
        result = await db.execute(
            delete(Post).where(and_(Post.id == post_id, Post.user_id == user_id))
        )
        await db.commit()
        return result.rowcount > 0  # type: ignore[attr-defined]
