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


# View Issue
class StGitlabIssueCommand(sublime_plugin.TextCommand):
    def run(self, edit, issue_id=None):

        if not issue_id:
            colsep = utils.stg_get_setting('table_column_separator')
            try:
                line = self.view.substr(self.view.line(self.view.sel()[0].end()))
                issue_id = line.split(colsep)[1].strip()
                int(issue_id)  # check is number
            except Exception as e:
                print('Exception: %s' % e)
                pass

        if not issue_id:
            issue_id = ''
            self.view.window().show_input_panel("Issue ID #:", issue_id, self.get_issue, None, None)
        else:
            self.get_issue(issue_id)

    def get_issue(self, text):
        self.view.run_command('st_gitlab_issue_fetcher', {'obj_id': text})


# Delete Issue
class StGitlabIssueDeleteCommand(sublime_plugin.TextCommand):
    def run(self, edit, issue_id=None):
        if not issue_id:
            try:
                line = self.view.substr(self.view.line(self.view.sel()[0].end()))
                issue_id = line.split('│')[1].strip()
                int(issue_id)  # check is number
            except Exception as e:
                print('Issue delete exception: %s' % e)

        if not issue_id:
            issue_id = ''
            self.view.window().show_input_panel("Issue ID (delete):", issue_id, self.delete_issue, None, None)
        else:
            self.delete_issue(issue_id)

    def delete_issue(self, issue_id):
        is_del = sublime.ok_cancel_dialog('Are you really want to delete issue #%s?' % issue_id)
        if not is_del:
            return
        project_id = self.view.settings().get('project_id', None)
        gitlab = StGitlab.connect()
        project = gitlab.projects.get(project_id)
        project.issues.delete(issue_id)
        if self.view.settings().get('screen', None) == 'st_gitlab_issues':
            self.view.run_command('st_gitlab_list_refresh')

