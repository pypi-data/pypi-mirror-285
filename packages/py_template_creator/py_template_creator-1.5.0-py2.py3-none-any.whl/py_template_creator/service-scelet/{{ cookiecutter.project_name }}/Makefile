SHELL := /bin/bash
include ../.env
export

env:
	pip install -r requirements/local.txt  > /dev/null

run:
	@echo "Running service..."
	python package/run.py

test:
	@echo "Running unit tests..."
	env POSTGRES_DB=test_db coverage run -m pytest ${module} && \
	coverage html && \
	coverage report
	@echo
	@echo "Flake8 errors in code ----------------"
	@echo
	@echo "--------------------------------------"
	@python -m flake8 --max-line-length=88 --exclude .git,__pycache__,.eggs,build
	@echo "OK, no flake8 errors in code"
	@echo "--------------------------------------"

lint:
	@python -m flake8 --max-line-length=88 --exclude .git,__pycache__,.eggs,build

migrations:
	@echo "Generating migrations ..."
	alembic -c ./package/alembic.ini revision --autogenerate -m "${message}"

migrate:
	@echo "Running migrations ..."
	alembic -c ./package/alembic.ini upgrade head
	@echo "Migrations finished."

downgrade:
	@echo "Running downgrade ..."
	alembic -c ./package/alembic.ini downgrade ${level}
	@echo "Migrations finished."

init_db:
	@echo "Initing database ..."
	alembic -c ./package/alembic.ini ensure_version
	@echo "Migrations finished."

check_db:
	@echo "Checking migrations ..."
	alembic -c ./package/alembic.ini check
	@echo "Migrations finished."
