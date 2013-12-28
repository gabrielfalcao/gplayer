#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright © 2013 GPlayer LLC
#
from __future__ import unicode_literals
import pprint
"""
gplayer.commands.core
~~~~~~~~~~~~~~~~~~~~~~

Contains commands for managing the http server in the local environment
"""

import sys
import logging

from flask.ext.script import Command
from werkzeug.serving import run_simple

from lineup.backends.redis import JSONRedisBackend
from gplayer.workers import OggPipeline


class RunServer(Command):  # pragma: no cover
    def __init__(self, application):
        self.application = application
        self.application.setup_logging(
            output=sys.stderr,
            level=logging.ERROR
        )

    def run(self):
        run_simple('0.0.0.0', 8000,
                   self.application,
                   use_reloader=True,
                   use_debugger=True,
        )


class Shell(Command):  # pragma: no cover
    def __init__(self, application):
        self.application = application
        self.application.setup_logging(
            output=sys.stderr,
            level=logging.DEBUG
        )

    def run(self):
        try:
            from IPython import embed
        except ImportError:
            sys.stderr.write(
                "You need to install \033[32mIPython\033[0m"
                " in order to use the gplayer shell\n")

        embed()


class RunWorker(Command):
    def __init__(self, application):
        self.application = application

    def run(self):
        pipeline = OggPipeline(JSONRedisBackend)
        pipeline._start()
        while pipeline.is_running():
            result = pipeline.output.get(wait=True)
            pprint.pprint(result)
