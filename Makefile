.PHONY: install migrate run up down collectstatic

install:
	python3 -m venv .venv
	. .venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt

migrate:
	. .venv/bin/activate && python src/manage.py migrate

run:
	. .venv/bin/activate && python src/manage.py runserver 0.0.0.0:8000

up:
	docker compose up --build

down:
	docker compose down

collectstatic:
	. .venv/bin/activate && python src/manage.py collectstatic --noinput
