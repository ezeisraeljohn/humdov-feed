run:
\tuvicorn app.main:app --reload

seed:
\tpython scripts/seed.py

test:
\tpytest -q
