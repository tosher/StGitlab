#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Phil Adams http://philadams.net

PNG file parser.
"""

# import logging
import struct


SIGNATURE = (b'\211PNG\r\n\032\n',)


class Chunk(object):
    """A PNG Chunk is composed of 4 fields:
        - a length (4 byte unsigned int)
        - a type (4 bytes, chars)
        - data (length bytes, various)
        - crc (4 bytes)
    Note: all integer values in PNG streams are big endian"""

    _length = struct.Struct('>L')
    _type = struct.Struct('cccc')
    _crc = 4
    _end_type = 'IEND'


class PNGFile(object):
    """A PNG Image"""

    def __init__(self, fp):
        self.fp = fp
        self.chunks = []
        self._load()
        self.header = self.chunks[0]['data']
        self.size = (self.header['width'], self.header['height'])

    def _load(self):

        # confirm PNG format
        magic = self.fp.read(len(SIGNATURE[0]))
        if magic != SIGNATURE[0]:
            # TODO: raise appropriate exception
            print('%s is not PNG signature' % magic)
            exit()
        self.content_type = 'image/png'

        # parse chunk stream
        l, t, c = Chunk._length, Chunk._type, Chunk._crc
        while True:

            # parse and store a chunk
            chunk = {}
            chunk['length'] = l.unpack(self.fp.read(l.size))[0]
            chunk['type'] = ''.join(['%s' % sc.decode() for sc in t.unpack(self.fp.read(t.size))])
            parse_data = '%s_data' % chunk['type']
            if hasattr(self, parse_data):
                chunk['data'] = getattr(self, parse_data)()
            else:
                chunk['data'] = self.fp.read(chunk['length'])
            chunk['crc'] = self.fp.read(c)
            self.chunks.append(chunk)

            # stop parsing if... we're at the end of the PNG file
            if chunk['type'] == Chunk._end_type:
                break
            # for now, we just need the IHDR chunk
            if chunk['type'] == 'IHDR':
                break

    def IHDR_data(self):
        dim = struct.Struct('>L')
        s = struct.Struct('c')
        data = {}
        data['width'] = dim.unpack(self.fp.read(dim.size))[0]
        data['height'] = dim.unpack(self.fp.read(dim.size))[0]
        data['bit_depth'] = ord(s.unpack(self.fp.read(s.size))[0])
        data['color_type'] = ord(s.unpack(self.fp.read(s.size))[0])
        data['compression_method'] = ord(s.unpack(self.fp.read(s.size))[0])
        data['filter_method'] = ord(s.unpack(self.fp.read(s.size))[0])
        data['interlace_method'] = ord(s.unpack(self.fp.read(s.size))[0])
        return data
