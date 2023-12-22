import os
from typing import AsyncGenerator, Generator

import pytest

from fastapi.testclient import TestClient
from httpx import AsyncClient

os.environ["ENV_STATE"] = "test"  # to run test in "test" mode

from database import database  # noqa: E402 <- avoid linter to send this line above the "os.envirion"
from main import app  # noqa: E402 <- avoid linter to send this line above the "os.envirion"


# This means it will run once per session
@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture()
def client() -> Generator:
    yield TestClient(app)


@pytest.fixture(autouse=True)
async def db() -> Generator:
    await database.connect()
    yield  # <- run the test function here
    await database.disconnect()


# Implement httpx to make the requests
@pytest.fixture()
async def async_client(client) -> AsyncGenerator:
    async with AsyncClient(app=app, base_url=client.base_url) as ac:
        yield ac
