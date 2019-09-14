
lint:
	poetry run pylama pyuubin tests

test:
	poetry run pytest --cov=pyuubin --cov=tests tests/