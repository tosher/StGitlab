#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

# import sublime
import sublime_plugin
from . import utils


class StGitlabUsersCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        # gitlab = utils.gl.get()
        per_page = utils.get_setting('list_page_size')
        query_params = {
            'page': 1,
            'per_page': per_page
        }
        title = 'Gitlab: Users'
        r = self.view.window().new_file()
        r.set_name(title)
        syntax_file = utils.get_setting('syntax_file')
        r.set_syntax_file(syntax_file)
        r.settings().set('query_params', query_params)
        r.settings().set('screen', utils.object_commands.get('user', {}).get('screen_list'))
        r.settings().set('object_name', 'user')
        r.settings().set("word_wrap", False)
        cmd = utils.object_commands.get('user', {}).get('list')
        r.run_command(cmd, {'title': title})
        r.set_scratch(True)
        r.set_read_only(True)
