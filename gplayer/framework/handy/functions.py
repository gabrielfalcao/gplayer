#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
from __future__ import unicode_literals

import re
import unicodedata
from datetime import datetime


def slugify(string):
    normalized = unicodedata.normalize("NFKD", string.lower())
    dashed = re.sub(r'\s+', '-', normalized)
    return re.sub(r'[^\w-]+', '', dashed)


def now():
    return datetime.utcnow()

def empty():
    return None
