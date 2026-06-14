import pytest
from httpx import AsyncClient

from app.models import User


@pytest.mark.asyncio
async def test_follow(test_user: User, test_client: AsyncClient, test_user2: User):
    response = await test_client.post(
        url=f"/api/users/{test_user2.id}/follow", headers={"api-key": test_user.api_key}
    )
    assert response.status_code == 200
    assert response.json() == {"result": True}


@pytest.mark.asyncio
async def test_unfollow(test_client: AsyncClient, test_user: User, test_user2: User):
    response = await test_client.post(
        url=f"/api/users/{test_user2.id}/follow", headers={"api-key": test_user.api_key}
    )
    assert response.status_code == 200

    response = await test_client.delete(
        url=f"api/users/{test_user2.id}/follow", headers={"api-key": test_user.api_key}
    )
    assert response.status_code == 200
    assert response.json() == {"result": True}


@pytest.mark.asyncio
async def test_follow_self(test_client: AsyncClient, test_user: User):
    response = await test_client.post(
        url=f"api/users/{test_user.id}/follow", headers={"api-key": test_user.api_key}
    )
    assert response.status_code == 200
    assert response.json() == {"result": False}


@pytest.mark.asyncio
async def test_no_users(test_client: AsyncClient, test_user: User):
    response = await test_client.post(
        url="api/users/9999/follow", headers={"api-key": test_user.api_key}
    )
    assert response.status_code == 404
    assert response.json()["result"] is False
