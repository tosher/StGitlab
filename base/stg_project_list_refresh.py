#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

import sublime
import sublime_plugin
from . import stg_utils as utils


class StGitlabProjectListRefreshCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        cursor = self.view.sel()[0]
        query_params = self.view.settings().get('query_params')
        per_page = utils.stg_get_setting('list_page_size')
        query_params['per_page'] = per_page
        if query_params:
            self.view.settings().set('query_params', query_params)
            title = self.view.name()
            self.view.set_read_only(False)
            self.view.erase(edit, sublime.Region(0, self.view.size()))
            object_name = self.view.settings().get('object_name')
            cmd = utils.object_commands.get(object_name, {}).get('list')
            self.view.run_command(cmd, {'title': title})
            self.view.sel().clear()
            self.view.sel().add(cursor)
            self.view.show(cursor)
            self.view.set_read_only(True)
            self.view.window().status_message('%ss list was refreshed.' % object_name.title())

    def is_visible(self, *args):
        screen = self.view.settings().get('screen')
        if not screen:
            return False
        valid_screens = [
            utils.object_commands.get('issue', {}).get('screen_list'),
            utils.object_commands.get('merge', {}).get('screen_list'),
            utils.object_commands.get('pipeline', {}).get('screen_list'),
            utils.object_commands.get('branch', {}).get('screen_list')
        ]

        if screen in valid_screens:
            return True
        return False
