#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

import re
import webbrowser
# import sublime
import sublime_plugin
from . import stg_utils as utils


# TODO: если несколько объектов в строке - показывать меню
class StGitlabUtilOpenUrlCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        utils.stg_validate_screen(['st_gitlab_issue', 'st_gitlab_merge'])

        # markdown urls
        try:
            text = self.view.substr(self.view.sel()[0])
            if re.findall(r'\]\((.*?)\)', text):
                url = self.view.substr(self.view.sel()[0]).split('(')[1].split(')')[0]
                if url:
                    if not url.startswith('http'):
                        gitlab = utils.gl.get()
                        project = gitlab.project()
                        project_name = project.attributes.get('path_with_namespace')
                        gl_url = utils.stg_get_setting('gitlab_url').rstrip('/')
                        url = '%s/%s/%s' % (gl_url, project_name, url.lstrip('/'))
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

        # issues
        try:
            text = self.view.substr(self.view.sel()[0])
            issues = re.findall(r'\#\d+', text)
            if issues:
                issue_id = issues[0][1:]
                self.view.run_command('st_gitlab_issue_fetcher', {'obj_id': issue_id})
        except Exception:
            pass

        # merge-requests
        try:
            text = self.view.substr(self.view.sel()[0])
            merges = re.findall(r'\!\d+', text)
            if merges:
                merge_id = merges[0][1:]
                self.view.run_command('st_gitlab_merge_fetcher', {'obj_id': merge_id})
        except Exception:
            pass

    def is_visible(self, *args):
        screen = self.view.settings().get('screen')
        if not screen:
            return False
        if screen in ['st_gitlab_issue', 'st_gitlab_merge']:
            return True
        return False
