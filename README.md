# Bong

Flask application scaffolding, modularized and 100% covered by unit
and functional tests; ready for extreme programming.

## Features

* SQLAlchemy support
* Simple ORM
* Command-line helpers through [flask-script](http://flask-script.readthedocs.org/)
* Easily create **application modules** *(analog to django apps)* through blueprints.
* WSGI container that sets up the plugins and blueprints
* Unique test DSL that looks turns writing tests into a more pleasant experience.
* Documentation support through [markment](http://falcao.it/markment)


## Getting Started

1. Fork the project
2. Clone from your own copy
3. Run the `install-wizard.sh` script, which will install the dependencies in your environment

3. Install dependencies through [curdling](http://clarete.li/curdling)
4. Rename the main module from `bong` to `whateveryouwant`
5. Run the `rename-inline` script with a mixed case name of your project:

```bash
rename-inline Bong WhateverYouWant
```

6. Run the tests to make sure everything went well
7. Disco!
