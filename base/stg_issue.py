#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

import sublime
import sublime_plugin
from . import stg_utils as utils
from .stg_gitlab import StGitlab
from .stg_project import ProjectSelectPanel


# Create Issue
class StGitlabIssueCreateCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        self.gitlab = StGitlab.connect()
        self.project_id = self.view.settings().get('project_id', None)
        if self.project_id:
            self.set_project(self.project_id)
        else:
            panel = ProjectSelectPanel(callback=self.set_project)
            panel.show_input()

    def set_project(self, project_id):
        self.project_id = project_id
        self.project = self.gitlab.projects.get(self.project_id)
        self.get_issue_title()

    def get_issue_title(self):
        self.view.window().show_input_panel("New issue title:", '', self.create_issue, None, None)

    def create_issue(self, title):
        issue = self.project.issues.create({'title': title})
        r = sublime.active_window().new_file()
        r.set_scratch(True)
        syntax_file = utils.stg_get_setting('syntax_file')
        r.set_syntax_file(syntax_file)
        r.settings().set('object_id', issue.iid)
        r.settings().set('project_id', self.project_id)
        r.run_command('st_gitlab_issue_fetcher', {'obj_id': issue.iid})


class StGitlabIssueCommand(sublime_plugin.TextCommand):

    INPUT_STR = 'Issue ID'

    def run(self, edit, obj_id=None):
        self.screen = self.view.settings().get('screen', None)
        if not obj_id:
            if self.screen == 'st_gitlab_issues':
                colsep = utils.stg_get_setting('table_column_separator')
                line = self.view.substr(self.view.line(self.view.sel()[0].end()))
                obj_id = line.split(colsep)[1].strip()
            elif self.screen == 'st_gitlab_issue':
                obj_id = self.view.settings().get('object_id', None)

        if not obj_id:
            self.view.window().show_input_panel(self.INPUT_STR, '', self.process, None, None)
        else:
            self.process(obj_id)

    def get_issue(self, obj_id):
        project_id = self.view.settings().get('project_id', None)
        gitlab = StGitlab.connect()
        project = gitlab.projects.get(project_id)
        return project.issues.get(obj_id)

    def refresh(self):
        if self.screen == 'st_gitlab_issues':
            self.view.run_command('st_gitlab_project_list_refresh')
        elif self.screen == 'st_gitlab_issue':
            self.view.close()

    def process(self, obj_id):
        if not obj_id:
            return
        self.view.run_command('st_gitlab_issue_fetcher', {'obj_id': obj_id})


class StGitlabIssueDeleteCommand(StGitlabIssueCommand):

    INPUT_STR = 'Issue ID to delete'

    def process(self, obj_id):
        if not obj_id:
            return
        is_del = sublime.ok_cancel_dialog('Are you really want to delete issue #%s?' % obj_id)
        if not is_del:
            return
        issue = self.get_issue(obj_id)
        issue.delete()
        self.refresh()

