run:
	uvicorn app.main:app --reload

lint:
	ruff app/

test:
	pytest tests/

scrape:
	python scripts/run_scraper.py