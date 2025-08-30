run:
	uvicorn app.main:app --reload

seed:
	python scripts/seed.py

test:
	pytest -q
