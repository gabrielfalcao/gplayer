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
	@[ "$(reset)" == "yes" ] && echo "drop database oggweed;create database oggweed" | mysql -uroot || echo "Running new migrations..."
	@alembic upgrade head

migrate-forward:
	echo "Running new migrations..."
	@alembic -c alembic.prod.ini upgrade head

local-migrate-back:
	@alembic downgrade -1

db:
	@echo "drop database if exists oggweed ;create database oggweed" | mysql -uroot
	python manage.py db

docs:
	markment -t .theme spec
	open "`pwd`/_public/index.html"

static:
	bower install
	@mkdir -p oggweed/static/{js,css,fonts}

	cp bower_components/angular/angular.min.js.map         oggweed/static/js
	cp bower_components/angular/angular.min.js             oggweed/static/js
	cp bower_components/jquery/jquery.min.js               oggweed/static/js
	cp bower_components/jquery/jquery.min.map              oggweed/static/js
	cp bower_components/bootstrap/dist/js/bootstrap.min.js oggweed/static/js

	cp bower_components/bootstrap/dist/fonts/*             oggweed/static/fonts

	cp bower_components/bootstrap/dist/css/*.min.css       oggweed/static/css

	cp bower_components/dropzone/downloads/dropzone.min.js oggweed/static/js
