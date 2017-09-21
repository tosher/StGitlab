#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

import sublime
import sublime_plugin
from . import stg_utils as utils
from .stg_project import ProjectSelectPanel
from .stg_gitlab import StGitlab


# Issues by project
class StGitlabProjectIssuesCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        panel = ProjectSelectPanel(callback=self.get_issues)
        panel.show_input()

    def get_issues(self, project_id):
        gitlab = StGitlab.connect()
        project = gitlab.projects.get(project_id)
        per_page = utils.stg_get_setting('list_page_size')
        query_params = {
            'project_id': project_id,
            'page': 1,
            'per_page': per_page,
            'state': 'opened'
        }
        title = 'Issues: %s' % project.name
        text = utils.stg_show_issues(title=title, **query_params)
        r = self.view.window().new_file()
        r.set_name(title)
        syntax_file = utils.stg_get_setting('syntax_file')
        r.set_syntax_file(syntax_file)
        r.settings().set('query_params', query_params)
        r.settings().set('screen', 'st_gitlab_issues')
        r.settings().set("word_wrap", False)
        r.settings().set("project_id", project_id)
        r.settings().set("page", 1)
        r.run_command('st_gitlab_insert_text', {'position': 0, 'text': text})
        r.set_scratch(True)
        # r.run_command('st_gitlab_view_show_labels')
        r.set_read_only(True)
