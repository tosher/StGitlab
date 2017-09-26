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
        screen = self.view.settings().get('screen', None)
        if screen == 'st_gitlab_issue':
            object_name = 'issue'
            obj = gitlab.issue()
        elif screen == 'st_gitlab_merge':
            object_name = 'merge'
            obj = gitlab.merge()

        obj.assignee_id = user_id
        obj.save()
        self.view.run_command('st_gitlab_object_refresh', {'object_name': object_name})
