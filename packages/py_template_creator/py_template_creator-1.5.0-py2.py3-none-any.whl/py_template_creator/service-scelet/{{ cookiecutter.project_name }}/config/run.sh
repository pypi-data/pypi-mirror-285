#!/usr/bin/env bash
alembic -c ./package/alembic.ini ensure_version
alembic -c ./package/alembic.ini upgrade head
{{ cookiecutter.project_name }}
