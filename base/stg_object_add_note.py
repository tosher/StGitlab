#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

import sublime
import sublime_plugin
from . import stg_utils as utils
from .stg_gitlab import StGitlab


# Issue comment input
class StGitlabObjectAddNoteCommand(sublime_plugin.TextCommand):

    def run(self, edit):

        utils.stg_validate_screen(
            [
                'st_gitlab_issue',
                'st_gitlab_merge'
            ]
        )

        self.view.window().show_input_panel('Note:', '', self.post_comment, None, None)

    def post_comment(self, text):
        object_id = self.view.settings().get('object_id', None)
        project_id = self.view.settings().get('project_id', None)
        if object_id and project_id:
            screen = self.view.settings().get('screen', None)
            gitlab = StGitlab.connect()
            project = gitlab.projects.get(project_id)
            if screen == 'st_gitlab_issue':
                object_name = 'issue'
                obj = project.issues.get(object_id)
            elif screen == 'st_gitlab_merge':
                object_name = 'merge'
                obj = project.mergerequests.get(object_id)
            obj.notes.create({'body': text})
            sublime.status_message('Note created successfully!')
            self.view.run_command('st_gitlab_object_refresh', {'object_name': object_name})
