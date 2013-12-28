#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
from __future__ import unicode_literals
from mock import patch
from oggweed.framework.handy.functions import slugify, empty, now



def test_slufify():
    ("slugify should turn everything inbto lower case and "
     "replace non-alphanumeric characters into dashes")

    slugify('Gabriel Falcão').should.equal('gabriel-falcao')


@patch('oggweed.framework.handy.functions.datetime')
def test_now_proxies_to_datetime_utcnow(datetime):
    ("api.models.now returns datetime.utcnow()")

    now().should.equal(datetime.utcnow.return_value)


def test_empty_returns_none():
    ("api.models.empty returns None")

    empty().should.be.none
