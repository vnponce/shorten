import pytest
from httpx import AsyncClient
from fastapi import status

from database import url_table, database
from libs.url import generate_url


async def create_url(url: str, async_client: AsyncClient) -> dict:
    response = await async_client.post("/shorten", json={"url": url})
    return response.json()


@pytest.mark.anyio
async def test_generate_url(async_client: AsyncClient):
    url_to_generate = "https://www.google.com/test-1"
    expected_url = generate_url(url_to_generate)

    response = await async_client.post("/shorten", json={"url": url_to_generate})

    assert response.status_code == status.HTTP_201_CREATED
    assert {"url": url_to_generate,
            "short_url": f"https://s.com/{expected_url}"}.items() <= response.json().items()


@pytest.mark.anyio
async def test_redirect_to_original_url(async_client: AsyncClient):
    url = "https://www.google.com/test-1"
    await create_url(url, async_client)
    short_code = generate_url(url)

    response = await async_client.get(f"/{short_code}")
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

    # avoid create a preexisting url record
    assert len(urls) == 1


@pytest.mark.anyio
async def test_avoid_short_code_collision(async_client: AsyncClient):
    preexisting_forced_url_1 = "https://www.google.com/test-1"
    preexisting_forced_url_2 = "https://www.google.com/test-2"
    colliding_url = "https://url-with-collision.com"

    duplicated_short_code = generate_url(colliding_url, size=32)

    # pre seed
    data = {"url": preexisting_forced_url_1, "short_code": duplicated_short_code[:7]}
    query = url_table.insert().values(data)
    await database.execute(query)
    # pre seed 2
    data = {"url": preexisting_forced_url_2, "short_code": duplicated_short_code[1:8]}
    query = url_table.insert().values(data)
    await database.execute(query)

    without_collision_record = await create_url(colliding_url, async_client)

    assert without_collision_record["short_code"] == duplicated_short_code[2:9]
