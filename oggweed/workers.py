#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
from __future__ import unicode_literals, absolute_import

import boto
import re
import time

import tempfile
import subprocess
from lineup.steps import Step
from lineup.framework import Pipeline
from plant import Node
from boto.s3.key import Key
from oggweed.web.models import Song

current_dir = Node(__file__).parent


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

        result = self.parse_result(stderr)

        result['final_path'] = final_path
        result['success'] = not failed
        return result

    def parse_result(self, output):
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
        result = audio.convert()
        instructions['result'] = result
        instructions['converted_at'] = time.time()
        self.produce(instructions)

    def rollback(self, instructions):
        print "\033[1;31m", instructions['__lineup__error__']['traceback'], "\033[0m"


class UploadS3(Step):
    def consume(self, instructions):
        filename = instructions['filename']
        key_name = '{0}:{1}'.format(time.time(), filename)

        original = instructions['result']['final_path']

        s3 = boto.connect_s3()
        bucket = s3.get_bucket('oggweed')

        key = Key(bucket, key_name)
        key.set_contents_from_filename(original)
        instructions['finalized_at'] = time.time()

        Song(**instructions).save()
        self.produce(instructions)

    def rollback(self, instructions):
        print "\033[1;31m", instructions['__lineup__error__']['traceback'], "\033[0m"


class OggPipeline(Pipeline):
    steps = [AnythingToOgg, UploadS3]
