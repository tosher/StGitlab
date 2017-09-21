#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

import sublime
import sublime_plugin
from . import stg_utils as utils
from .stg_gitlab import StGitlab
from .stg_user import UserSelectPanel


# Project objects filter
class StGitlabProjectListFilterCommand(sublime_plugin.TextCommand):

    query_params = {}
    filter_name = None
    filter_values = []
    project_id = None

    def run(self, edit):
        utils.stg_validate_screen(
            [
                'st_gitlab_issues',
                'st_gitlab_merges',
                'st_gitlab_pipelines'
            ]
        )
        self.filter_types = utils.filter_types
        self.project_id = self.view.settings().get('project_id', None)
        self.view.window().show_quick_panel(list(self.filter_types.keys()), self.filter_done)

    def filter_done(self, filter_id):
        if filter_id < 0:
            return

        filter_type_key = list(self.filter_types.keys())[filter_id]
        self.filter_name = self.filter_types[filter_type_key]
        gitlab = StGitlab.connect()
        project = gitlab.projects.get(self.project_id)

        self.filter_values = []
        if self.filter_name in ['author_id', 'assignee_id']:
            panel = UserSelectPanel(callback=self.filter_user_done)
            panel.show_input()
            return
        elif self.filter_name == 'labels':
            self.filter_values = [label.name for label in project.labels.list(all=True)]
            filter_names = self.filter_values
        elif self.filter_name == 'milestone':
            self.filter_values = [mile.title for mile in project.milestones.list(all=True)]
            filter_names = self.filter_values
        elif self.filter_name == 'state':
            self.filter_values = filter_names = ['opened', 'closed']
        elif filter_type_key == 'Reset filters':
            query_params = self.view.settings().get('query_params', {})
            keys = list(query_params.keys())
            for key in keys:
                if key in list(self.filter_types.values()):
                    del query_params[key]
            self.get_list(query_params)
            sublime.status_message('All filters was cleared.')
            return

        if self.filter_values:
            self.view.window().show_quick_panel(filter_names, self.filter_select_done)
        else:
            self.view.window().show_input_panel("Search:", '', self.filter_input_done, None, None)

    def filter_user_done(self, user_id):
        query_params = self.view.settings().get('query_params', {})
        query_params[self.filter_name] = user_id
        self.get_list(query_params)

    def filter_input_done(self, text):
        if not text:
            return
        query_params = self.view.settings().get('query_params', {})
        filter_value = text
        if self.filter_name == 'page':
            filter_value = int(text)

        query_params[self.filter_name] = filter_value
        self.get_list(query_params)

    def filter_select_done(self, idx):
        if idx < 0:
            return
        filter_value = self.filter_values[idx]
        query_params = self.view.settings().get('query_params', {})
        if self.filter_name == 'labels':
            if self.filter_name in query_params:
                if filter_value not in query_params[self.filter_name]:
                    query_params[self.filter_name].append(filter_value)
            else:
                query_params[self.filter_name] = [filter_value]
        else:
            query_params[self.filter_name] = filter_value

        self.get_list(query_params)

    def get_list(self, query_params):
        per_page = utils.stg_get_setting('list_page_size')
        query_params['per_page'] = per_page
        query_params['state'] = 'opened'
        if self.filter_name != 'page':
            query_params['page'] = 1
        self.view.settings().set('query_params', query_params)
        self.view.run_command('st_gitlab_project_list_refresh')

