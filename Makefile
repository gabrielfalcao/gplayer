all: test

test: unit functional

prepare:
	@pip install -q curdling
	@curd install -r development.txt

clean:
	@git clean -Xdf # removing files that match patterns inside .gitignore

unit:
	@python manage.py unit

functional: db
	@python manage.py functional

acceptance:
	@python manage.py acceptance

shell:
	python manage.py shell

run:
	python manage.py run

check:
	python manage.py check


local-migrate-forward:
	@[ "$(reset)" == "yes" ] && echo "drop database bong;create database bong" | mysql -uroot || echo "Running new migrations..."
	@alembic upgrade head

migrate-forward:
	echo "Running new migrations..."
	@alembic -c alembic.prod.ini upgrade head

local-migrate-back:
	@alembic downgrade -1

db:
	@echo "drop database if exists bong ;create database bong" | mysql -uroot
	python manage.py db

docs:
	markment -t .theme spec
	open "`pwd`/_public/index.html"
