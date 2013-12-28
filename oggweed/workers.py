#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import re
import os
import boto

import time
import logging

from boto.s3.connection import Location

import tempfile
import subprocess
from lineup.steps import Step
from lineup.framework import Pipeline
from plant import Node
from boto.s3.key import Key
from oggweed.web.models import Song

current_dir = Node(__file__).parent


log = logging.getLogger('goloka:workers:s3')


class S3Worker(Step):
    @property
    def conn(self):
        return self.get_connection()

    def get_connection(self):
        return boto.connect_s3()

index_html = """
<html>
  <head><title>Index for {repository[full_name]}</title>
<link href='http://fonts.googleapis.com/css?family=Share+Tech+Mono' rel='stylesheet' type='text/css'>
<style type="text/css">
* font-family: "Share Tech Mono";
</style>
  </head>
  <body><h2>Welcome to {repository[full_name]}</h2>
  <footer>goloka</footer>
  </body>
</html>"""

error_html = """
<html>
  <head><title>Error</title>
<link href='http://fonts.googleapis.com/css?family=Share+Tech+Mono' rel='stylesheet' type='text/css'>
<style type="text/css">
* font-family: "Share Tech Mono";
</style>
  </head>
  <body><h2>Error in {repository[full_name]}</h2>
  <footer>goloka</footer>
  </body>
</html>"""


class UploadS3(S3Worker):
    def get_bucket_name(self, instructions):
        return 'oggweed'

    def get_bucket(self, instructions):
        bucket_name = self.get_bucket_name(instructions)
        bucket = self.conn.lookup(bucket_name)
        log.info("Bucket lookup: %s %s", bucket_name, bucket)
        return bucket

    def get_or_create_bucket(self, instructions):
        bucket_name = self.get_bucket_name(instructions)
        bucket = self.get_bucket(instructions)
        if not bucket:
            bucket = self.conn.create_bucket(bucket_name,
                                             location=Location.USWest,
                                             policy='public-read')
            self.log("Bucket created: %s", bucket)

        bucket.make_public(recursive=True)
        return bucket

    def get_filename(self, instructions):
        filename = instructions['filename']
        return os.path.split(filename)[-1]

    def store_file(self, instructions):
        local_source_path = instructions['metadata']['final_path']

        key_local_path = os.path.split(local_source_path)[-1]
        token = instructions['token']

        key_name = '{0}:{1}'.format(token, key_local_path)
        bucket = self.get_bucket(instructions)

        key = Key(bucket, key_name)

        def progress_callback(sent, total):
            self.backend.set(
                "song:{0}:s3:progress".format(token),
                "{0}/{1}".format(sent, total))

        key.set_contents_from_filename(local_source_path, cb=progress_callback)
        key.make_public()
        instructions['url'] = key.generate_url(
            0, query_auth=False, force_http=True)

        print 'url', instructions['url'], key, key.key

        instructions['finalized_at'] = time.time()
        instructions['metadata'].update({
            'key_name': key_name,
        })
        return instructions

    def consume(self, instructions):
        update_and = self.store_file(instructions)
        Song(**update_and).save()
        self.produce(instructions)

    def rollback(self, instructions):
        print ("\033[1;31m",
               instructions['__lineup__error__']['traceback'],
               "\033[0m")


class ConversionError(Exception):
    pass


class OggConverter(object):
    def __init__(self, source_filename):
        self.source_filename = source_filename
        self.output = None

    def get_args(self, final_path):
        return [
            '/usr/local/bin/ffmpeg',
            '-loglevel', 'info',
            '-i', self.source_filename,
            '-strict', '-2', '-acodec', 'vorbis',
            '-ab', '450k', '-q', '10', '-y',
            final_path
        ]

    def convert(self, final_path=None):
        final_path = final_path or self.source_filename + b'.ogg'
        stderr = tempfile.TemporaryFile()

        command = self.get_args(final_path)
        failed = subprocess.call(command, stderr=stderr)
        if failed:
            stderr.seek(0)
            raise ConversionError(stderr.read())

        metadata = self.parse_metadata(stderr)
        metadata['final_path'] = final_path
        return metadata

    def parse_metadata(self, output):
        output.seek(0)
        # Duration: 00:07:58.00, start: 0.000000, bitrate: 1411 kb/s
        regex = re.compile(b'Duration: ([\d:]+).*bitrate:\s*(.*[/]s)')
        found = regex.search(output.read())
        if found:
            duration = found.group(1)
            bitrate = found.group(2)
            return {
                'duration': duration,
                'bitrate': bitrate,
            }
        else:
            return {}


class AnythingToOgg(Step):
    def consume(self, instructions):
        source_filename = instructions['filename']
        audio = OggConverter(source_filename)
        metadata = audio.convert()

        instructions['metadata'] = metadata
        instructions['converted_at'] = time.time()
        self.produce(instructions)

    def rollback(self, instructions):
        print "\033[1;31m", instructions['__lineup__error__']['traceback'], "\033[0m"


class OggPipeline(Pipeline):
    steps = [AnythingToOgg, UploadS3]
