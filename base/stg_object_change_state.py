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

            obj.state_event = self.state_events[state_idx]
            obj.save()
            self.view.run_command('st_gitlab_object_refresh', {'object_name': object_name})

        utils.stg_validate_screen(
            [
                'st_gitlab_issue',
                'st_gitlab_merge'
            ]
        )

        gitlab = StGitlab()
        screen = self.view.settings().get('screen', None)
        if screen == 'st_gitlab_issue':
            object_name = 'issue'
            obj = gitlab.issue()
        elif screen == 'st_gitlab_merge':
            object_name = 'merge'
            obj = gitlab.merge()

        self.view.window().show_quick_panel(self.states, on_done)
