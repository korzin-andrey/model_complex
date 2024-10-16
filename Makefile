run:
	poetry run python -B test.py

remove_cache:
	find . -name "__pycache__" -type d -exec rm -rf {} +