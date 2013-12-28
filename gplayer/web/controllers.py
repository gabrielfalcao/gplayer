#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright © 2013 Propellr LLC
#
from __future__ import unicode_literals

import json
from gplayer import settings
from flask import (
    Blueprint,
    render_template,
    session,
    url_for,
    request,
    redirect,
)
from lineup.backends.redis import JSONRedisBackend
from gplayer.workers import OggPipeline
from werkzeug.utils import secure_filename
from gplayer.web.models import Song

module = Blueprint('web.controllers', __name__)


@module.context_processor
def inject_basics():
    return dict(
        settings=settings,
        messages=session.pop('messages', []),
        github_user=session.get('github_user_data', None),
        json=json,
        len=len,
        full_url_for=lambda *args, **kw: settings.absurl(
            url_for(*args, **kw)
        ),
        ssl_full_url_for=lambda *args, **kw: settings.sslabsurl(
            url_for(*args, **kw)
        ),
        static_url=lambda path: "{0}/{1}".format(
            settings.STATIC_BASE_URL.rstrip('/'),
            path.lstrip('/')
        ),
    )


@module.route('/')
def index():
    return render_template('index.html')


@module.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    filename = secure_filename(file.filename)
    destination = settings.UPLOADED_FILE(filename)
    file.save(destination)

    song = Song.from_filename(destination)
    song.save()

    pipeline = OggPipeline(JSONRedisBackend)
    pipeline.input.put(song.as_dict())

    return redirect(url_for('.song',
                            token=song.token))


@module.route('/song/<token>')
def song(token):
    song = Song.from_token(token)
    return render_template('song.html', song=song)
