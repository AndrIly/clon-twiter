import pytest
from httpx import AsyncClient

from app.models import User


@pytest.mark.asyncio
async def test_get_me(test_client: AsyncClient, test_user: User):
    response = await test_client.get(
        "api/users/me", headers={"api-key": test_user.api_key}
    )
    assert response.status_code == 200
    assert response.json()["user"]["name"] == test_user.username
    assert response.json()["user"]["id"] == test_user.id
    assert isinstance(response.json()["user"]["followers"], list)
    assert isinstance(response.json()["user"]["following"], list)


@pytest.mark.asyncio
async def test_get_me_no_key(test_client: AsyncClient):
    response = await test_client.get("api/users/me", headers={"api-key": ""})
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_followers_in_profile(
    test_client: AsyncClient, test_user: User, test_user2: User
):
    response = await test_client.post(
        url=f"api/users/{test_user2.id}/follow", headers={"api-key": test_user.api_key}
    )
    assert response.status_code == 200
    response = await test_client.get(
        "api/users/me", headers={"api-key": test_user2.api_key}
    )
    assert response.status_code == 200
    followers = response.json()["user"]["followers"]
    assert len(followers) == 1
    assert followers[0]["id"] == test_user.id
    assert followers[0]["name"] == test_user.username
    response = await test_client.get(
        "api/users/me", headers={"api-key": test_user.api_key}
    )
    following = response.json()["user"]["following"]
    assert len(following) == 1
    assert following[0]["id"] == test_user2.id
    assert following[0]["name"] == test_user2.username


@pytest.mark.asyncio
async def test_get_user_404(test_client: AsyncClient, test_user: User):
    response = await test_client.get("api/users/me", headers={"api-key": "hello"})
    assert response.status_code == 401
