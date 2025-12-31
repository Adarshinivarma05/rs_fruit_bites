.PHONY: install run test format lint clean migrate upgrade help

help:
	@echo "RS Fruit Bites - Available Commands"
	@echo "===================================="
	@echo "install    - Install dependencies with Poetry"
	@echo "run        - Run the Streamlit application"
	@echo "test       - Run tests with pytest"
	@echo "format     - Format code with black"
	@echo "lint       - Lint code with ruff"
	@echo "clean      - Clean cache and temporary files"
	@echo "migrate    - Create new database migration"
	@echo "upgrade    - Apply database migrations"
	@echo "init-db    - Initialize database tables"

install:
	poetry install

run:
	poetry run streamlit run app.py

test:
	poetry run pytest tests/ -v --cov=src

format:
	poetry run black src/ tests/ app.py

lint:
	poetry run ruff check src/ tests/ app.py

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +

migrate:
	poetry run alembic revision --autogenerate -m "$(msg)"

upgrade:
	poetry run alembic upgrade head

init-db:
	poetry run python -c "from src.core.database import init_db; init_db()"
