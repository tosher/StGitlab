#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Phil Adams http://philadams.net

GIF file parser.
"""

# import logging
import struct


SIGNATURE = ('GIF87a', 'GIF89a')


class GIFFile(object):
    """A GIF Image"""

    def __init__(self, fp):
        self.fp = fp
        self.size = None  # set by _load()
        self._load()

    def _load(self):

        # confirm GIF format
        magic = self.fp.read(len(SIGNATURE[0]))
        if magic not in SIGNATURE:
            # TODO: raise appropriate exception
            print('%s is not GIF signature' % magic)
            exit()
        self.content_type = 'image/gif'
        hw = struct.Struct('h')
        x = hw.unpack(self.fp.read(2))[0]
        y = hw.unpack(self.fp.read(2))[0]
        self.size = (x, y)
