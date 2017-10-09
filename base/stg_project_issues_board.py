#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

# import sublime
import sublime_plugin
from . import stg_utils as utils
from .stg_project import ProjectSelectPanel


class StGitlabProjectIssuesBoardCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        panel = ProjectSelectPanel(callback=self.get_issues)
        panel.show_input()

    def get_issues(self, project_id):
        gitlab = utils.gl.get()
        project = gitlab.project(oid=project_id)
        per_page = utils.stg_get_setting('list_page_size')
        query_params = {
            'project_id': project_id,
            'page': 1,
            'per_page': per_page,
            'state': 'opened'
        }
        title = 'Issues Board: %s' % project.name
        r = self.view.window().new_file()
        r.set_name(title)
        syntax_file = utils.stg_get_setting('syntax_file')
        r.set_syntax_file(syntax_file)
        r.settings().set('query_params', query_params)
        r.settings().set('screen', utils.object_commands.get('issue', {}).get('screen_board'))
        r.settings().set('object_name', 'issue')
        r.settings().set("word_wrap", False)
        r.settings().set("project_id", project_id)
        # cmd = utils.object_commands.get('issue', {}).get('list')
        r.run_command('st_gitlab_project_issues_board_draw', {'title': title})
        r.set_scratch(True)
        # r.run_command('st_gitlab_view_show_labels')
        r.set_read_only(True)
