#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

import re
import webbrowser
# import sublime
import sublime_plugin
from . import stg_utils as utils


class StGitlabUtilOpenUrlCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        utils.stg_validate_screen(['st_gitlab_issue', 'st_gitlab_merge'])

        # markdown urls
        try:
            url = self.view.substr(self.view.sel()[0]).split('(')[1].split(')')[0]
            if url:
                if not url.startswith('http'):
                    gl_url = utils.stg_get_setting('gitlab_url').rstrip('/')
                    url = '%s/%s' % (gl_url, url.lstrip('/'))
                webbrowser.open(url)
                return
        except Exception:
            pass

        # just urls
        try:
            text = self.view.substr(self.view.sel()[0])
            urls = re.findall(r'(https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*))', text)
            if urls:
                url = urls[0][0]
                webbrowser.open(url)
        except Exception:
            pass
