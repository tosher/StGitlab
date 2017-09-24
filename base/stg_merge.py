#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

from .stg_object import StGitlabObjectCommand


class StGitlabMergeCommand(StGitlabObjectCommand):

    INPUT_STR = 'Merge-request ID'
    SCREEN_LIST = 'st_gitlab_merges'
    SCREEN_VIEW = 'st_gitlab_merge'
    FETCHER = 'st_gitlab_merge_fetcher'
