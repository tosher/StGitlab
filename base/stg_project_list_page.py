#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

import sublime
import sublime_plugin
from . import stg_utils as utils


class StGitlabProjectListPageCommand(sublime_plugin.TextCommand):
    def run(self, edit, direction):

        utils.stg_validate_screen(
            [
                'st_gitlab_issues',
                'st_gitlab_merges',
                'st_gitlab_pipelines'
            ]
        )

        query_params = self.view.settings().get('query_params')
        per_page = utils.stg_get_setting('list_page_size')
        page = query_params.get('page', 1)
        if direction:
            page += 1
        else:
            page -= 1
            page = page if page >= 1 else 1
        query_params['page'] = page
        query_params['per_page'] = per_page
        self.view.settings().set('query_params', query_params)

        if query_params:
            title = self.view.name()

            screen = self.view.settings().get('screen', None)
            if screen == 'st_gitlab_issues':
                text = utils.stg_show_issues(title=title, **query_params)
            elif screen == 'st_gitlab_merges':
                text = utils.stg_show_merges(title=title, **query_params)
            elif screen == 'st_gitlab_pipelines':
                text = utils.stg_show_pipelines(title=title, **query_params)

            self.view.set_read_only(False)
            self.view.erase(edit, sublime.Region(0, self.view.size()))
            self.view.run_command('st_gitlab_insert_text', {'position': 0, 'text': text})
            self.view.set_read_only(True)
