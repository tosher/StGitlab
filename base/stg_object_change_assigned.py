#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

# import sublime
import sublime_plugin
from . import stg_utils as utils
from .stg_user import UserSelectPanel


class StGitlabObjectChangeAssignedCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        panel = UserSelectPanel(callback=self.assign)
        panel.show_input()

    def assign(self, user_id):
        gitlab = utils.gl.get()
        obj = gitlab.object_by_view()
        gitlab.assignee_set(user_id, obj)
        self.view.run_command('st_gitlab_object_refresh')

    def is_visible(self, *args):
        screen = self.view.settings().get('screen')
        if not screen:
            return False
        valid_screens = [
            utils.object_commands.get('issue', {}).get('screen_view'),
            utils.object_commands.get('merge', {}).get('screen_view')
        ]
        if screen in valid_screens:
            return True
        return False

