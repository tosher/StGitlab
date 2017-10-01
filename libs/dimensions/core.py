#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Phil Adams http://philadams.net

A pure Python library for reading the width and height of PNG images.

See README.txt for details.
"""

import logging
# import struct
from io import BytesIO

from . import PNGFile
from . import GIFFile
from . import JPEGFile


def get_dimensions_from_stream(datastream):
    """given a image datastream, compute dimensions
    return sequence of tuples (x, y, content-type, filename)"""

    fp = BytesIO(datastream)
    implemented = False
    img_types = (PNGFile, GIFFile, JPEGFile)
    for img_type in img_types:
        sig = img_type.SIGNATURE[0]
        magic = fp.read(len(sig))
        fp.seek(0)
        if magic == sig:
            cls = img_type.__name__.split('.')[-1]
            img = getattr(img_type, cls)(fp)
            x, y = img.size
            return (x, y, img.content_type)

    if not implemented:
        # might want to fail silently, or print error to stdout...
        # print('cannot handle file: %s' % filename)
        raise NotImplementedError


def get_dimensions(filenames, as_stream=False):
    """given a sequence of filenames, compute dimensions
    return sequence of tuples (x, y, content-type, filename)"""

    dims = []
    for filename in filenames:
        implemented = False
        with open(filename, 'rb') as fp:

            img_types = (PNGFile, GIFFile, JPEGFile)
            for img_type in img_types:
                sig = img_type.SIGNATURE[0]
                magic = fp.read(len(sig))
                fp.seek(0)
                if magic == sig:
                    cls = img_type.__name__.split('.')[-1]
                    img = getattr(img_type, cls)(fp)
                    x, y = img.size
                    dims.append((x, y, img.content_type, filename))
                    implemented = True
                    break
            if not implemented:
                # might want to fail silently, or print error to stdout...
                print('cannot handle file: %s' % filename)
                raise NotImplementedError
    return dims


def dimensions(filenames):
    """given a filename or list of filenames,
    return a tuple or sequence of tuples (x, y, filename)"""

    single = type(filenames) is str
    if single:
        filenames = [filenames]
    dims = get_dimensions(filenames)
    if single:
        dims = dims[0]
    return dims


def cli():
    import argparse

    # populate and parse command line options
    desc = 'Read the width and height of images.'
    desc += '\nhttp://github.com/philadams/dimensions'
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('-v', '--verbose', action='count', default=0)
    parser.add_argument('filenames', nargs='+',
            help='source image(s)')
    args = parser.parse_args()

    # logging config
    log_level = logging.WARNING  # default
    if args.verbose == 1:
        log_level = logging.INFO
    elif args.verbose >= 2:
        log_level = logging.DEBUG
    logging.basicConfig(level=log_level)

    dims = get_dimensions(args.filenames)
    for x, y, content_type, filename in dims:
        print('%s\n  width: %d\n  height: %d\n  content-type: %s' % (filename, x, y, content_type))

if '__main__' == __name__:
    dimensions()
