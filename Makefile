lint:
	poetry run isort quantum_web
	poetry run ruff quantum_web
	poetry run mypy quantum_web

fix:
