#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

import sublime
import sublime_plugin
from . import stg_utils as utils
from .stg_gitlab import StGitlab
from .stg_project import ProjectSelectPanel

# TODO: TEST required


# Issue: move to project
class StGitlabChangeProjectCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        def on_done(project_id_new):
            if issue_id:
                project = gitlab.projects.get(project_id)
                project_new = gitlab.projects.get(project_id_new)
                issue = project.issues.get(issue_id)
                issue.move(project_id_new)
                issue.save()
                self.view.settings().set('project_id', project_id_new)
                sublime.status_message('Issue #%r is moved to %s' % (issue.id, project_new.name))
                self.view.run_command('st_gitlab_issue_fetcher', {'obj_id': issue_id})

        # validate
        utils.stg_validate_screen('st_gitlab_issue')

        gitlab = StGitlab.connect()
        issue_id = self.view.settings().get('object_id', None)
        project_id = self.view.settings().get('project_id', None)
        if project_id and issue_id:
            panel = ProjectSelectPanel(callback=on_done)
            panel.show_input()

