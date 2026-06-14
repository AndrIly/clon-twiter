from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Follow


class FollowServices:
    @staticmethod
    async def add_follow(db: AsyncSession, follower_id: int, following_id: int):
        if follower_id == following_id:
            return None

        unique = await db.execute(
            select(Follow).where(
                Follow.follower_id == follower_id, Follow.following_id == following_id
            )
        )

        if unique.one_or_none():
            return None

        follow = Follow(follower_id=follower_id, following_id=following_id)
        db.add(follow)
        await db.commit()
        return follow

    @staticmethod
    async def remove_follow(
        db: AsyncSession, follower_id: int, following_id: int
    ) -> bool:
        search_follow = await db.execute(
            select(Follow).where(
                Follow.follower_id == follower_id, Follow.following_id == following_id
            )
        )

        if not search_follow.one_or_none():
            return False

        await db.execute(
            delete(Follow).where(
                Follow.following_id == following_id, Follow.follower_id == follower_id
            )
        )
        await db.commit()
        return True
