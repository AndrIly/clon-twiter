import pytest
from httpx import AsyncClient

from app.models import User


@pytest.mark.asyncio
async def test_upload_media(test_client: AsyncClient, test_user: User):
    files = {"file": ("test.png", b"fakeimagebytes", "image/png")}
    response = await test_client.post(
        "api/medias", files=files, headers={"api-key": test_user.api_key}
    )
    assert response.status_code == 200
    assert response.json()["media_id"] == 1


@pytest.mark.asyncio
async def test_tweet_with_media(test_client: AsyncClient, test_user: User):
    files = {"file": ("test.png", b"fakeimagebytes", "image/png")}
    response = await test_client.post(
        "api/medias", files=files, headers={"api-key": test_user.api_key}
    )
    media_id = response.json()["media_id"]

    response = await test_client.post(
        "api/tweets",
        json={"tweet_data": "test content", "tweet_media_ids": [media_id]},
        headers={"api-key": test_user.api_key},
    )
    tweet_id = response.json()["tweet_id"]
    assert response.status_code == 201
    assert response.json()["result"] is True

    response = await test_client.get(
        f"api/tweets/{tweet_id}", headers={"api-key": test_user.api_key}
    )
    assert response.status_code == 200
    assert len(response.json()["attachments"]) == 1
