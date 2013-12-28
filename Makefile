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
	@[ "$(reset)" == "yes" ] && echo "drop database gplayer;create database gplayer" | mysql -uroot || echo "Running new migrations..."
	@alembic upgrade head

migrate-forward:
	echo "Running new migrations..."
	@alembic -c alembic.prod.ini upgrade head

local-migrate-back:
	@alembic downgrade -1

db:
	@echo "drop database if exists gplayer ;create database gplayer" | mysql -uroot
	python manage.py db

docs:
	markment -t .theme spec
	open "`pwd`/_public/index.html"

static:
	bower install
	@mkdir -p gplayer/static/{js,css,fonts}

	cp bower_components/angular/angular.min.js.map         gplayer/static/js
	cp bower_components/angular/angular.min.js             gplayer/static/js
	cp bower_components/jquery/jquery.min.js               gplayer/static/js
	cp bower_components/jquery/jquery.min.map              gplayer/static/js
	cp bower_components/bootstrap/dist/js/bootstrap.min.js gplayer/static/js

	cp bower_components/bootstrap/dist/fonts/*             gplayer/static/fonts

	cp bower_components/bootstrap/dist/css/*.min.css       gplayer/static/css

	cp bower_components/dropzone/downloads/dropzone.min.js gplayer/static/js
