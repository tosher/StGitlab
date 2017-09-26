#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

import sublime
import sublime_plugin
from . import stg_utils as utils


class StGitlabObjectSetMilestoneCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        def on_done(index):
            if index < 0:
                return
            if index == 0:
                obj.milestone_id = None
            else:
                obj.milestone_id = milestones[index - 1].id
            obj.save()
            self.view.run_command('st_gitlab_object_refresh', {'object_name': object_name})

        utils.stg_validate_screen(
            [
                'st_gitlab_issue',
                'st_gitlab_merge'
            ]
        )

        gitlab = utils.gl.get()
        milestones = []
        milestones_menu = ['[Remove]']
        screen = self.view.settings().get('screen', None)
        if screen == 'st_gitlab_issue':
            object_name = 'issue'
            obj = gitlab.issue()
        elif screen == 'st_gitlab_merge':
            object_name = 'merge'
            obj = gitlab.merge()

        milestones = gitlab.milestones(state='active')

        if milestones:
            for mile in milestones:
                milestones_menu.append(mile.title)
            sublime.set_timeout(lambda: sublime.active_window().show_quick_panel(milestones_menu, on_done), 1)
