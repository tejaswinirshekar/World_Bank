import asyncio
from app.scraper.fetch import scrape_worldbank_countries
from app.db.models import Country
from app.db.session import engine, Session

async def main():
    countries = await scrape_worldbank_countries()
    with Session(engine) as session:
        for c in countries:
            country = Country(name=c["name"], url=c["url"])
            session.add(country)
        session.commit()

if __name__ == "__main__":
    asyncio.run(main())