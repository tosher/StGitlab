#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

import sublime_plugin
from . import stg_utils as utils
from .stg_gitlab import StGitlab


class StGitlabObjectChangeStateCommand(sublime_plugin.TextCommand):
    states = ['opened', 'closed']
    state_events = ['reopen', 'close']

    def run(self, edit):
        def on_done(state_idx):
            if state_idx < 0:
                return

            if object_id:
                obj.state_event = self.state_events[state_idx]
                obj.save()
                self.view.run_command('st_gitlab_object_refresh', {'object_name': object_name})

        utils.stg_validate_screen(
            [
                'st_gitlab_issue',
                'st_gitlab_merge'
            ]
        )

        gitlab = StGitlab.connect()
        object_id = self.view.settings().get('object_id', None)
        project_id = self.view.settings().get('project_id', None)
        if project_id and object_id:
            screen = self.view.settings().get('screen', None)
            project = gitlab.projects.get(project_id)
            if screen == 'st_gitlab_issue':
                object_name = 'issue'
                obj = project.issues.get(object_id)
            elif screen == 'st_gitlab_merge':
                object_name = 'merge'
                obj = project.mergerequests.get(object_id)

            self.view.window().show_quick_panel(self.states, on_done)
