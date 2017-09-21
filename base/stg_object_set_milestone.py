#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

import sublime
import sublime_plugin
from . import stg_utils as utils
from .stg_gitlab import StGitlab


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

        gitlab = StGitlab.connect()
        milestones = []
        milestones_menu = ['[Remove]']
        object_id = self.view.settings().get('object_id', None)
        project_id = self.view.settings().get('project_id', None)

        if object_id and project_id:
            screen = self.view.settings().get('screen', None)
            project = gitlab.projects.get(project_id)
            if screen == 'st_gitlab_issue':
                object_name = 'issue'
                obj = project.issues.get(object_id)
            elif screen == 'st_gitlab_merge':
                object_name = 'merge'
                obj = project.mergerequests.get(object_id)

            milestones = project.milestones.list(state='active')

            if milestones:
                for mile in milestones:
                    milestones_menu.append(mile.title)
                sublime.set_timeout(lambda: sublime.active_window().show_quick_panel(milestones_menu, on_done), 1)
