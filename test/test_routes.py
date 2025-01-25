import pytest
from httpx import AsyncClient

@pytest.mark.asynco
async def test_root(ac: AsyncClient):
    responce = await ac.get("/")
    assert responce.status_code == 200
