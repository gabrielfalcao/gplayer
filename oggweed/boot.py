#!/usr/bin/env python
# -*- coding: utf-8 -*-
# <Copyright 2013 - OggWeed LLC>
from __future__ import unicode_literals

"""Boot file for the application

# please notice that nothing in this file it indispensable for the
# real application to run: session, assets and stuff like that is
# encapsulated within the `from_env()` method because then, by being
# inside of a class method, it becomes easier to achieve 100% of test
# coverage and also results in good isolation of responsabilities.

THIS FILE MUST NEVER BE IMPORTED IN PRODUCTION
"""
from oggweed.server import application


# Importing core commands
from oggweed.framework.commands.core import (
    RunServer,
    Shell,
    RunWorker,
)

# Importing db commands
from oggweed.framework.commands.db import (
    CreateDB,
)

# Importing testing commands
from oggweed.framework.commands.testing import (
    RunTest,
    RunAcceptanceTests,
)

# Registering user commands
application.enable_commands([
    # Testing-related commands
    ('unit', RunTest('unit')),
    ('functional', RunTest('functional')),
    ('acceptance', RunAcceptanceTests()),

    # Testing-related commands
    ('run', RunServer(application)),
    ('shell', Shell(application)),
    ('converter-pipeline', RunWorker(application)),

    # DB commands
    ('db', CreateDB(application)),
])
