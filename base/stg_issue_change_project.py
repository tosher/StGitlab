#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

import sublime
import sublime_plugin
from . import stg_utils as utils
from .stg_project import ProjectSelectPanel


class StGitlabChangeProjectCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        def on_done(project_id_new):
            if not project_id_new:
                return
            project_new = gitlab.project(oid=project_id_new)
            issue.move(project_id_new)
            self.view.settings().set('project_id', project_new.id)
            self.view.settings().set('object_id', issue.iid)
            sublime.status_message('Issue #%r was moved to %s' % (issue.id, project_new.name))
            self.view.run_command('st_gitlab_object_refresh')

        utils.stg_validate_screen('st_gitlab_issue')

        gitlab = utils.gl.get()
        project = gitlab.project()
        issue = gitlab.issue()
        if project and issue:
            panel = ProjectSelectPanel(callback=on_done)
            panel.show_input()

