#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

# import sublime
import sublime_plugin
from . import stg_utils as utils
from .stg_user import UserSelectPanel


class StGitlabObjectChangeAssignedCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        utils.stg_validate_screen(
            [
                'st_gitlab_issue',
                'st_gitlab_merge'
            ]
        )

        panel = UserSelectPanel(callback=self.assign)
        panel.show_input()

    def assign(self, user_id):
        gitlab = utils.gl.get()
        obj = gitlab.object_by_view()
        gitlab.assignee_set(user_id, obj)
        self.view.run_command('st_gitlab_object_refresh')
