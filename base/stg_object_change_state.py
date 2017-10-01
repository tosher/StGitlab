#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

import sublime_plugin
from . import stg_utils as utils


class StGitlabObjectChangeStateCommand(sublime_plugin.TextCommand):
    states = ['opened', 'closed']
    state_events = ['reopen', 'close']

    def run(self, edit):
        def on_done(state_idx):
            if state_idx < 0:
                return

            obj.state_event = self.state_events[state_idx]
            obj.save()
            self.view.run_command('st_gitlab_object_refresh')

        utils.stg_validate_screen(
            [
                'st_gitlab_issue',
                'st_gitlab_merge'
            ]
        )

        gitlab = utils.gl.get()
        obj = gitlab.object_by_view()
        self.view.window().show_quick_panel(self.states, on_done)
