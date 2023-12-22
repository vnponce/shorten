import pytest
from httpx import AsyncClient
from fastapi import status

from libs.url import generate_url


@pytest.mark.anyio
async def test_generate_url(async_client: AsyncClient):
    url_to_generate = "https://www.google.com/test-1"
    expected_url = generate_url(url_to_generate)

    response = await async_client.post("/url-shortener", json={"url": url_to_generate})

    assert response.status_code == status.HTTP_201_CREATED
    short_url = response.json()["short_url"]
    assert {"id": 1, "url": url_to_generate, "short_url": expected_url}.items() <= response.json().items()
