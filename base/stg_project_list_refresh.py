#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

import sublime
import sublime_plugin
from . import stg_utils as utils
# from .stg_gitlab import StGitlab


# Project lists refresh
class StGitlabProjectListRefreshCommand(sublime_plugin.TextCommand):
    def run(self, edit):

        utils.stg_validate_screen(
            [
                'st_gitlab_issues',
                'st_gitlab_merges',
                'st_gitlab_pipelines'
            ]
        )
        query_params = self.view.settings().get('query_params')
        per_page = utils.stg_get_setting('list_page_size')
        query_params['per_page'] = per_page
        if query_params:
            self.view.settings().set('query_params', query_params)
            title = self.view.name()
            screen = self.view.settings().get('screen', None)
            self.view.erase_phantoms('label')
            if screen == 'st_gitlab_issues':
                text = utils.stg_show_issues(title=title, **query_params)
            elif screen == 'st_gitlab_merges':
                text = utils.stg_show_merges(title=title, **query_params)
            elif screen == 'st_gitlab_pipelines':
                text = utils.stg_show_pipelines(title=title, **query_params)
            self.view.set_read_only(False)
            # self.view.erase_phantoms('label')
            self.view.erase(edit, sublime.Region(0, self.view.size()))
            self.view.run_command('st_gitlab_insert_text', {'position': 0, 'text': text})
            # self.view.run_command('st_gitlab_view_show_labels')
            self.view.set_read_only(True)
