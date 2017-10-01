#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

import sublime
import sublime_plugin
from . import stg_utils as utils


class StGitlabProjectListPageCommand(sublime_plugin.TextCommand):
    def run(self, edit, direction):
        utils.stg_validate_screen(
            [
                utils.object_commands.get('issue', {}).get('screen_list'),
                utils.object_commands.get('merge', {}).get('screen_list'),
                utils.object_commands.get('pipeline', {}).get('screen_list'),
                utils.object_commands.get('branch', {}).get('screen_list')
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
            object_name = self.view.settings().get('object_name', None)
            self.view.set_read_only(False)
            self.view.erase_phantoms('shortcuts')
            self.view.erase(edit, sublime.Region(0, self.view.size()))
            cmd = utils.object_commands.get(object_name, {}).get('list')
            self.view.run_command(cmd, {'title': title})
            # self.view.erase_phantoms('label')
            self.view.set_read_only(True)
