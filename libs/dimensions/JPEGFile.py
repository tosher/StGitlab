#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Phil Adams http://philadams.net

JPG file parser.
"""

# import logging
import struct
# import StringIO
# from io import BytesIO

# SIGNATURE = ('\377\330')
SIGNATURE = (b'\xff\xd8',)


class JPEGFile(object):
    """A JPEG Image"""

    def __init__(self, fp):
        # self.fp = StringIO.StringIO(str(fp.read()))
        self.fp = fp
        self.size = None  # set by _load()
        self._load()

    def _load(self):

        # confirm JPEG format
        magic = self.fp.read(len(SIGNATURE[0]))
        if magic not in SIGNATURE[0]:
            # TODO: raise appropriate exception
            print('%s is not a JPG signature' % magic)
            exit()
        self.content_type = 'image/jpeg'

        x, y = -1, -1
        b = self.fp.read(1)
        try:
            while (b and ord(b) != 0xDA):  # start of image data itself
                # get to marker start
                while (ord(b) != 0xFF):
                    b = self.fp.read(1)
                # read marker start, and any repeated padding
                while (ord(b) == 0xFF):
                    b = self.fp.read(1)
                # if marker type is SOF0, SOF1, SOF2, read x, y
                if (ord(b) >= 0xC0 and ord(b) <= 0xC3):
                    self.fp.read(3)  # skip payload len
                    y, x = struct.unpack('>HH', self.fp.read(4))
                    break
                else:  # skip over the length of this segment payload
                    self.fp.read(int(struct.unpack('>H', self.fp.read(2))[0]) - 2)
                b = self.fp.read(1)
            self.size = (int(x), int(y))
        except struct.error:
            pass
        except ValueError:
            pass
