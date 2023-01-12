lint:
	poetry run isort fix quantum_web
	poetry run ruff quantum_web
	poetry run mypy quantum_web

fix:
