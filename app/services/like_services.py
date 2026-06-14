from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.functions import count

from app.models.like import Like
from app.models.post import Post


class LikeService:
    @staticmethod
    async def add_like(db: AsyncSession, user_id: int, post_id: int) -> Like | None:
        result = await db.execute(
            select(Like).where(Like.user_id == user_id).where(Like.post_id == post_id)
        )
        existing_like = result.scalar_one_or_none()
        if existing_like:
            return None
        like = Like(user_id=user_id, post_id=post_id)
        db.add(like)
        post_result = await db.execute(select(Post).where(Post.id == post_id))
        post = post_result.scalar_one_or_none()
        if post is None:
            return None
        post.likes_count = post.likes_count + 1
        await db.commit()
        await db.refresh(post)
        await db.refresh(like)
        return like

    @staticmethod
    async def remove_like(db: AsyncSession, user_id: int, post_id: int) -> bool:
        like = await db.execute(
            select(Like).where(Like.user_id == user_id).where(Like.post_id == post_id)
        )
        if like.scalar_one_or_none():
            post_result = await db.execute(select(Post).where(Post.id == post_id))
            post = post_result.scalar_one_or_none()
            if post is None:
                return False
            post.likes_count = post.likes_count - 1
            await db.execute(
                delete(Like)
                .where(Like.user_id == user_id)
                .where(Like.post_id == post_id)
            )
            await db.commit()
            await db.refresh(post)
            return True
        else:
            return False

    @staticmethod
    async def get_likes_count(db: AsyncSession, post_id: int) -> int:
        like = await db.execute(
            select(count(Like.id)).select_from(Like).where(Like.post_id == post_id)
        )
        result = like.scalar_one_or_none()
        return result if result else 0
