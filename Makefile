lint:
	poetry run isort quantum_web
	poetry run ruff quantum_web
	poetry run mypy quantum_web

test:
	docker compose exec api coverage run manage.py test

coverage: test
	docker compose exec api coverage xml
	docker compose exec api coverage report -m --skip-covered
