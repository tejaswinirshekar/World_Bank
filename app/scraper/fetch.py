import httpx
from selectolax.parser import HTMLParser

async def scrape_worldbank_countries():
    url = "https://data.worldbank.org/country"
    async with httpx.AsyncClient() as client:
        resp = await client.get(url)
        html = HTMLParser(resp.text)
        countries = []
        for a in html.css('a'):
            href = a.attributes.get("href", "")
            if "/country/" in href:
                countries.append({
                    "name": a.text(strip=True),
                    "url": f"https://data.worldbank.org{href}"
                })
        return countries