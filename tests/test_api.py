import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_get_country_graph():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/countries/India/gdp-graph")
    assert response.status_code == 200
    assert "<div" in response.text  # Contains HTML chart