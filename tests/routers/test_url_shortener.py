import pytest
from httpx import AsyncClient
from fastapi import status

from database import url_table, database
from libs.url import generate_url


async def create_url(url: str, async_client: AsyncClient) -> dict:
    response = await async_client.post("/url-shortener", json={"url": url})
    return response.json()


@pytest.mark.anyio
async def test_generate_url(async_client: AsyncClient):
    url_to_generate = "https://www.google.com/test-1"
    expected_url = generate_url(url_to_generate)

    response = await async_client.post("/url-shortener", json={"url": url_to_generate})

    assert response.status_code == status.HTTP_201_CREATED
    assert {"url": url_to_generate, "short_code": expected_url}.items() <= response.json().items()


@pytest.mark.anyio
async def test_redirect_to_original_url(async_client: AsyncClient):
    url = "https://www.google.com/test-1"
    await create_url(url, async_client)
    short_code = generate_url(url)

    response = await async_client.get(f"/url-shortener/{short_code}")
    assert response.status_code == status.HTTP_200_OK

    data = response.json()

    assert url == data


@pytest.mark.anyio
async def test_return_preexisting_url(async_client: AsyncClient):
    url = "https://www.google.com/test-1"
    await create_url(url, async_client)

    # send preexisting url
    await create_url(url, async_client)

    query = url_table.select()
    urls = await database.fetch_all(query)

    # avoid create an preexisting url record
    assert len(urls) == 1
