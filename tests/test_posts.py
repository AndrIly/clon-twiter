import pytest
from httpx import AsyncClient

from app.models.post import Post
from app.models.users import User


@pytest.mark.asyncio
async def test_get_feed(test_client: AsyncClient, test_user: User):
    response = await test_client.get(
        "api/tweets", headers={"api-key": test_user.api_key}
    )
    assert response.status_code == 200
    assert response.json()["result"] is True
    assert isinstance(response.json().get("tweets"), list)


@pytest.mark.asyncio
async def test_create_post(test_client: AsyncClient, test_user: User):
    response = await test_client.post(
        "api/tweets",
        json={"tweet_data": "test content"},
        headers={"api-key": test_user.api_key},
    )
    assert response.status_code == 201
    assert isinstance(response.json()["tweet_id"], int)


@pytest.mark.asyncio
async def test_get_post_by_id(
    test_client: AsyncClient, test_post: Post, test_user: User
):
    response = await test_client.get(
        f"api/tweets/{test_post.id}", headers={"api-key": test_user.api_key}
    )
    assert response.status_code == 200
    assert isinstance(response.json(), dict)


@pytest.mark.asyncio
async def test_delete_post(test_client: AsyncClient, test_user: User, test_post: Post):
    response = await test_client.delete(
        f"api/tweets/{test_post.id}", headers={"api-key": test_user.api_key}
    )
    assert response.status_code == 200
    assert response.json() == {"result": True}


@pytest.mark.asyncio
async def test_feed_only_followed(
    test_client: AsyncClient, test_user: User, test_user2: User
):
    response = await test_client.post(
        "api/tweets",
        json={"tweet_data": "test content"},
        headers={"api-key": test_user2.api_key},
    )
    assert response.status_code == 201

    response = await test_client.get(
        "api/tweets", headers={"api-key": test_user.api_key}
    )
    assert response.status_code == 200
    assert response.json()["tweets"] == []

    response = await test_client.post(
        f"api/users/{test_user2.id}/follow", headers={"api-key": test_user.api_key}
    )
    assert response.status_code == 200
    assert response.json()["result"] is True

    response = await test_client.get(
        "api/tweets", headers={"api-key": test_user.api_key}
    )
    author = response.json()["tweets"][0]["author"]["id"]
    assert response.status_code == 200
    assert response.json()["tweets"] != []
    assert author == test_user2.id


@pytest.mark.asyncio
async def test_feed_sorted_by_likes(test_client: AsyncClient, test_user: User):
    await test_client.post(
        "api/tweets",
        json={"tweet_data": "content 2"},
        headers={"api-key": test_user.api_key},
    )
    response = await test_client.post(
        "api/tweets",
        json={"tweet_data": "test content"},
        headers={"api-key": test_user.api_key},
    )
    tweet_id = response.json()["tweet_id"]
    assert response.status_code == 201

    response = await test_client.post(
        f"api/tweets/{tweet_id}/likes", headers={"api-key": test_user.api_key}
    )
    assert response.status_code == 200

    response = await test_client.get(
        "api/tweets", headers={"api-key": test_user.api_key}
    )

    tweets = response.json()["tweets"]
    assert response.status_code == 200
    assert len(tweets) == 2
    assert tweets[0]["id"] == tweet_id
