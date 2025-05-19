from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import HTMLResponse
from fastapi_cache.decorator import cache
import httpx
import pandas as pd
import plotly.express as px

router = APIRouter()

# ✅ 1. List all continents
@router.get("/continents", summary="List all continents", tags=["Helper"])
async def list_continents():
    return [
        "East Asia & Pacific",
        "Europe & Central Asia",
        "Latin America & Caribbean",
        "Middle East & North Africa",
        "North America",
        "South Asia",
        "Sub-Saharan Africa"
    ]

# ✅ 2. List countries (optionally by continent)
@router.get("/countries", summary="List countries (optionally filtered by continent)", tags=["Country"])
@cache(expire=86400)
async def list_countries(continent: str = Query(None, description="Optional continent name to filter countries")):
    url = "http://api.worldbank.org/v2/country?format=json&per_page=500"

    async with httpx.AsyncClient() as client:
        response = await client.get(url)

    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Failed to fetch countries")

    data = response.json()
    if len(data) < 2:
        return []

    countries = data[1]

    if continent:
        countries = [c for c in countries if c.get("region", {}).get("value") == continent]

    return [
        {
            "id": c["id"],  # e.g., "IN"
            "name": c["name"],  # e.g., "India"
            "region": c["region"]["value"],
            "income_level": c["incomeLevel"]["value"],
            "capital": c.get("capitalCity"),
            "latitude": c.get("latitude"),
            "longitude": c.get("longitude")
        }
        for c in countries if c["region"]["value"] != "Aggregates"
    ]

# ✅ 3. Get country details by ID
@router.get("/countries/{country_id}", summary="Get full details for a country", tags=["Country"])
@cache(expire=86400)
async def get_country_detail(country_id: str):
    url = f"http://api.worldbank.org/v2/country/{country_id}?format=json"

    async with httpx.AsyncClient() as client:
        response = await client.get(url)

    if response.status_code != 200:
        raise HTTPException(status_code=404, detail="Country not found")

    data = response.json()
    if len(data) < 2 or not data[1]:
        raise HTTPException(status_code=404, detail="No data found")

    return data[1][0]

# ✅ 4. Get graph for a country and indicator
@router.get("/countries/{country_id}/graph", response_class=HTMLResponse, summary="Get indicator graph for a country", tags=["Country"])
@cache(expire=3600)
async def get_indicator_graph(country_id: str, indicator: str = "NY.GDP.PCAP.CD"):
    url = f"http://api.worldbank.org/v2/country/{country_id.lower()}/indicator/{indicator}?format=json&per_page=100"

    async with httpx.AsyncClient() as client:
        response = await client.get(url)

    if response.status_code != 200:
        raise HTTPException(status_code=404, detail="Country or indicator not found")

    data = response.json()
    if len(data) < 2 or not data[1]:
        raise HTTPException(status_code=404, detail="No indicator data available")

    df = pd.DataFrame(data[1])
    df = df[["date", "value"]].dropna()
    df["date"] = pd.to_datetime(df["date"])
    df.sort_values("date", inplace=True)

    fig = px.line(df, x="date", y="value", title=f"{indicator} for {country_id.upper()}")
    return fig.to_html(full_html=False)