import asyncio

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models.post import Post
from app.models.users import User

TEST_DATA_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def test_engine():
    engine = create_async_engine(
        TEST_DATA_URL,
        echo=False,
        future=True,
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture
async def test_sessionmaker(test_engine):
    return async_sessionmaker(test_engine, expire_on_commit=False, class_=AsyncSession)


@pytest.fixture
async def test_db(test_sessionmaker):
    async with test_sessionmaker() as session:
        yield session


@pytest.fixture
async def test_client(test_sessionmaker):
    async def override_get_db():
        async with test_sessionmaker() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as c:
        yield c

    app.dependency_overrides.clear()


@pytest.fixture
async def test_user(test_db):
    user = User(
        api_key="test_api_key",
        username="test_username",
        email="test@example.com",
        is_active=True,
    )

    test_db.add(user)
    await test_db.commit()
    await test_db.refresh(user)
    return user


@pytest.fixture
async def test_post(test_db, test_user):
    post = Post(
        content="test content",
        user_id=test_user.id,
        likes_count=0,
    )
    test_db.add(post)
    await test_db.commit()
    await test_db.refresh(post)

    return post


@pytest.fixture
async def test_user2(test_db):
    user = User(api_key="key2", username="second_user", is_active=True)
    test_db.add(user)
    await test_db.commit()
    await test_db.refresh(user)
    return user
