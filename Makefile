set_autoformatting:
	pre-commit install

remove_cache:
	find . -name "__pycache__" -type d -exec rm -rf {} +

install:
	poetry install --with dev

add:
	poetry add ${NAME}

add_dev:
	poetry add --group dev ${NAME}
