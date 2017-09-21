#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

# import sublime
import sublime_plugin
from . import stg_utils as utils
from .stg_gitlab import StGitlab


# Issue description
class StGitlabObjectChangeDescriptionCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        def on_done(text):
            if text:
                if object_id:
                    obj.description = text
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
        if object_id:
            screen = self.view.settings().get('screen', None)
            project = gitlab.projects.get(project_id)
            if screen == 'st_gitlab_issue':
                object_name = 'issue'
                obj = project.issues.get(object_id)
            elif screen == 'st_gitlab_merge':
                object_name = 'merge'
                obj = project.mergerequests.get(object_id)
            description = obj.description if obj.description else ''
            self.view.window().show_input_panel("Description:", description, on_done, None, None)
