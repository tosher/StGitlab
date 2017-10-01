#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

from .stg_object import StGitlabObjectCommand


class StGitlabMergeCommand(StGitlabObjectCommand):

    INPUT_STR = 'Merge-request ID'
    object_name = 'merge'
