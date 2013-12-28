#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
from __future__ import unicode_literals
import time
from datetime import datetime
from hashlib import sha1


import json
import bcrypt
import sqlalchemy as db

from oggweed import settings
from oggweed.framework.db import Model, metadata, get_redis_connection
from oggweed.framework.log import get_logger

from oggweed.framework.handy.functions import now


logger = get_logger('oggweed.web.models')


class User(Model):
    table = db.Table(
        'user', metadata,
        db.Column('id', db.Integer, primary_key=True),
        db.Column('email', db.String(100), nullable=False, unique=True),
        db.Column('password', db.String(128), nullable=False),
        db.Column('created_at', db.DateTime, default=now),
    )

    def to_dict(self):
        data = self.to_dict_original()
        data.pop('password')
        return data

    @classmethod
    def authenticate(cls, email, password):
        user = cls.find_one_by(email=email)

        if not user:
            return

        if user.password == cls.secretify_password(password):
            return user

    @classmethod
    def secretify_password(cls, plain):
        salt = 'pr0p3l'
        salted = salt.join(str(plain))
        return bcrypt.hashpw(salted, settings.SALT)

    @classmethod
    def create(cls, email, password):
        password = cls.secretify_password(password)
        return super(User, cls).create(email=email, password=password)


class Song(object):
    keys = (
        'filename',
        'uploaded_at',
        'converted_at',
        'finalized_at',
        'day',
        'metadata',
        'url',
        'token',
    )

    @classmethod
    def from_filename(cls, filename):
        today = datetime.now().strftime("%Y-%m-%d")
        token = sha1(filename + today + 'oggweed').hexdigest()
        song_data = {
            'filename': filename,
            'uploaded_at': time.time(),
            'converted_at': None,
            'day': today,
            'token': token,
        }
        new = cls(**song_data)
        return new

    def __init__(self, **kw):
        self.__data__ = {}
        for key in self.keys:
            setattr(self, key, None)

        for key, value in kw.items():
            self.__data__[key] = value
            setattr(self, key, value)

    def as_dict(self):
        d = {}
        for k in self.keys:
           d[k] = getattr(self, k, None)

        return d

    def as_json(self):
        return json.dumps(self.as_dict())

    def save(self):
        redis = get_redis_connection()

        if not self.finalized_at:
            keys_to_push = [
                "list:songs:all",
                "list:songs:{0}".format(self.day)
            ]
        else:
            keys_to_push = [
                "list:songs:ready",
            ]

        for key in keys_to_push:
            redis.rpush(key, "song:{0}".format(self.token))

        redis.set("song:{0}".format(self.token), self.as_json())

    @classmethod
    def from_token(cls, token):
        redis = get_redis_connection()
        raw = redis.get("song:{0}".format(token))
        data = json.loads(raw)
        return cls(**data)
