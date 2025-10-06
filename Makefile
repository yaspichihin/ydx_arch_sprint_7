.PHONY: format


format:
	isort .
	ruff check .