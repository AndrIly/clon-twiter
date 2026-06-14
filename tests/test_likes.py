import pytest
from httpx import AsyncClient

from app.models.post import Post
from app.models.users import User


@pytest.mark.asyncio
async def test_post_like(test_post: Post, test_client: AsyncClient, test_user: User):

    response = await test_client.post(
        f"api/tweets/{test_post.id}/likes", headers={"api-key": test_user.api_key}
    )

    assert response.status_code == 200
    assert response.json() == {"result": True}


@pytest.mark.asyncio
async def test_unlike_like(test_post: Post, test_client: AsyncClient, test_user: User):
    response = await test_client.post(
        f"api/tweets/{test_post.id}/likes", headers={"api-key": test_user.api_key}
    )
    assert response.status_code == 200
    response = await test_client.delete(
        f"api/tweets/{test_post.id}/likes", headers={"api-key": test_user.api_key}
    )
    assert response.status_code == 200
    assert response.json() == {"result": True}


@pytest.mark.asyncio
async def test_like_like(test_post: Post, test_client: AsyncClient, test_user: User):
    response = await test_client.post(
        f"api/tweets/{test_post.id}/likes", headers={"api-key": test_user.api_key}
    )
    assert response.status_code == 200
    twice_response = await test_client.post(
        f"api/tweets/{test_post.id}/likes", headers={"api-key": test_user.api_key}
    )
    assert twice_response.status_code == 404
