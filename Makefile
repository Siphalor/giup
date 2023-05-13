.PHONY: license-headers

license-headers:
	poetry install && poetry run -- licensify HEADER --directory giup --exclude __init__.py
