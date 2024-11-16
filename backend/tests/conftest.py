import os
from collections.abc import AsyncGenerator, Generator

import pytest
from faker import Faker
from fastapi.testclient import TestClient
from sqlmodel.ext.asyncio.session import AsyncSession
from supabase._async.client import create_client

from app.core.db import engine
from app.main import app
from app.schemas import Token


@pytest.fixture(scope="module")
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture(scope="module")
async def db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSession(engine) as session:
        yield session


@pytest.fixture(scope="module")
def client() -> Generator[TestClient, None, None]:
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="module")
async def token() -> AsyncGenerator[Token, None]:
    url = os.environ.get("SUPABASE_TEST_URL")
    assert url is not None, "Must provide SUPABASE_TEST_URL environment variable"
    key = os.environ.get("SUPABASE_TEST_KEY")
    assert key is not None, "Must provide SUPABASE_TEST_KEY environment variable"
    db_client = await create_client(url, key)
    fake_email = Faker().email()
    fake_password = Faker().password()
    response = await db_client.auth.sign_up(
        {"email": fake_email, "password": fake_password}
    )
    assert response.user
    assert response.user.email == fake_email
    assert response.user.id is not None

    yield Token(access_token=response.session.access_token)
