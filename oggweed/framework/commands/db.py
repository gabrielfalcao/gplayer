#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright © 2013 OggWeed LLC
#
from __future__ import unicode_literals, absolute_import

"""
oggweed.commands.db
~~~~~~~~~~~~~~~~~~~~~~

Contains commands for handling db stuff in the local environment
"""

import os
from flask.ext.script import Command



class CreateDB(Command):  # pragma: no cover
    def __init__(self, application):
        self.application = application

    def run(self):
        print "Creating database `oggweed`"
        os.system('echo "DROP DATABASE IF EXISTS oggweed" | mysql -uroot ')
        os.system('echo "CREATE DATABASE oggweed" | mysql -uroot ')
        print "Running migrations"
        os.system('alembic upgrade head')
