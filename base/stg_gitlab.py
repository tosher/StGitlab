#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

import sys
import os
import sublime
sys.path.append(os.path.join(os.path.dirname(__file__), "../libs"))
import gitlab


class StGitlab:
    def connect():
        settings = sublime.load_settings("StGitlab.sublime-settings")
        url = settings.get('gitlab_url')
        api_key = settings.get('api_token')
        # TODO: request use for ssl validation
        # requests = settings.get('connection_options')
        return gitlab.Gitlab(url, api_key, api_version=4)
