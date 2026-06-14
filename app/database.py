import os
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

if os.path.exists(".env"):
    from dotenv import load_dotenv

    load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql+asyncpg://admin:admin@localhost:5432/clon_twitter_db"
)


class Base(DeclarativeBase):
    pass


# engine = create_async_engine(DATABASE_URL, echo=False, future=True)

engine = None

# AsyncSessionLocal = async_sessionmaker(
#     engine, class_=AsyncSession, expire_on_commit=False
# )


async def get_engine():
    global engine
    if engine is None:
        engine = create_async_engine(DATABASE_URL, future=True, echo=False)
    return engine


AsyncSessionLocal: async_sessionmaker[AsyncSession] | None = None


async def init_sessionmaker():
    global AsyncSessionLocal
    if AsyncSessionLocal is None:
        eng = await get_engine()
        AsyncSessionLocal = async_sessionmaker(
            eng, class_=AsyncSession, expire_on_commit=False
        )


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    await init_sessionmaker()
    assert AsyncSessionLocal is not None
    async with AsyncSessionLocal() as session:
        yield session


async def init_db():
    eng = await get_engine()
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await _seed_default_user()


async def _seed_default_user() -> None:
    from sqlalchemy import select

    await init_sessionmaker()
    assert AsyncSessionLocal is not None
    async with AsyncSessionLocal() as session:
        from app.models.follow import Follow
        from app.models.post import Post
        from app.models.users import User

        defaults = {"test": "user", "test2": "alice"}
        users: dict[str, User] = {}
        for api_key, username in defaults.items():
            res = await session.execute(select(User).where(User.api_key == api_key))
            existing = res.scalar_one_or_none()
            if existing is None:
                existing = User(api_key=api_key, username=username, is_active=True)
                session.add(existing)
            users[api_key] = existing
        await session.commit()
        for u in users.values():
            await session.refresh(u)

        posts = await session.execute(select(Post).limit(1))
        if posts.scalar_one_or_none() is None:
            session.add_all(
                [
                    Post(content="Первый пост", user_id=users["test"].id),
                    Post(
                        content="Теперь я буду видеть ",
                        user_id=users["test"].id,
                    ),
                    Post(content="Новый пользователь", user_id=users["test2"].id),
                ]
            )
            await session.commit()
        follow = await session.execute(select(Follow).limit(1))
        if follow.scalar_one_or_none() is None:
            session.add_all(
                [
                    Follow(
                        follower_id=users["test"].id, following_id=users["test2"].id
                    ),
                    Follow(
                        follower_id=users["test2"].id, following_id=users["test"].id
                    ),
                ]
            )
            await session.commit()


async def close_db():
    if engine:
        await engine.dispose()
