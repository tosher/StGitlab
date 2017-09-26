#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

import sublime
import sublime_plugin
from . import stg_utils as utils
from .stg_project import ProjectSelectPanel
from .stg_object import StGitlabObjectCommand


# Create Issue
class StGitlabIssueCreateCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        self.gitlab = utils.gl.get()
        self.project_id = self.view.settings().get('project_id', None)
        if self.project_id:
            self.set_project(self.project_id)
        else:
            panel = ProjectSelectPanel(callback=self.set_project)
            panel.show_input()

    def set_project(self, project_id):
        self.project_id = project_id
        self.project = self.gitlab.project(oid=self.project_id)
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


class StGitlabIssueCommand(StGitlabObjectCommand):

    INPUT_STR = 'Issue ID'
    SCREEN_LIST = 'st_gitlab_issues'
    SCREEN_VIEW = 'st_gitlab_issue'
    FETCHER = 'st_gitlab_issue_fetcher'

    def get_issue(self):
        return self.gitlab.issue(project_id=self.project_id, oid=self.obj_id)


class StGitlabIssueDeleteCommand(StGitlabIssueCommand):

    INPUT_STR = 'Issue ID to delete'

    def refresh(self):
        if self.screen == 'st_gitlab_issues':
            self.view.run_command('st_gitlab_project_list_refresh')
        elif self.screen == 'st_gitlab_issue':
            self.view.close()

    def process(self):
        if not self.obj_id:
            return
        is_del = sublime.ok_cancel_dialog('Are you really want to delete issue #%s?' % self.obj_id)
        if not is_del:
            return
        issue = self.get_issue()
        issue.delete()
        self.refresh()

