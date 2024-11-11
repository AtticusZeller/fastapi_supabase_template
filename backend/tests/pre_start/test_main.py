import pytest
from fastapi.testclient import TestClient


@pytest.mark.anyio
async def test_read_main(client: TestClient) -> None:
    response = client.get("/docs")
    assert response.status_code == 200
