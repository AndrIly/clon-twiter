import pytest
from httpx import AsyncClient

from app.models import User


@pytest.mark.asyncio
async def test_error_format(test_client: AsyncClient, test_user: User):
    response = await test_client.post(
        "api/users/9999/follow", headers={"api-key": test_user.api_key}
    )
    assert response.status_code == 404
    assert response.json()["result"] is False
    assert response.json()["error_type"] == "HTTPException"
    assert response.json()["error_message"] == "User not found"
