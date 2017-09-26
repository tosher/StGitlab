#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

import sys
import os
# import sublime
import sublime_plugin
from collections import OrderedDict
from . import stg_utils as utils
from .stg_html import StShortcutsMenu
sys.path.append(os.path.join(os.path.dirname(__file__), "../libs"))
from terminaltables.other_tables import WindowsTable as SingleTable


class StGitlabProjectObjectsListCommand(sublime_plugin.TextCommand):

    shortcuts = {}

    def run(self, edit, title):
        self.title = title
        self.gitlab = utils.gl.get()
        self.query_params = self.view.settings().get('query_params', {})
        self.objects = self.get_objects()
        self.build()

    def build(self):
        self.show_shortcuts()
        content = '\n'
        content += self.show_header()
        content += self.show_filters()
        content += self.show_table()
        self.view.run_command('st_gitlab_insert_text', {'position': 0, 'text': content})
        self.view.show(0)

    def show_shortcuts(self):
        StShortcutsMenu(self.view, self.shortcuts, None)

    def show_header(self):
        header = '\n'
        header += '## %s\n' % self.title
        header += '\t**Total**: %s\n' % len(self.objects)
        page = self.query_params.get('page')
        per_page = self.query_params.get('per_page')
        header += '\t**Page number**: %(page)s (%(per_page)s issues per page)\n' % {
            'page': page,
            'per_page': per_page
        }
        return header

    def show_filters(self):
        filters = '\t**Filters**:\n'
        for name in utils.filter_types.values():
            if name in self.query_params:
                if name == 'labels':
                    lbl_char = utils.stg_get_setting('label_char')
                    labels = ', '.join(['%(lbl_char)s%(label)s%(lbl_char)s' % {'lbl_char': lbl_char, 'label': label} for label in self.query_params.get(name)])
                    filters += '\t\t**%s**: %s\n' % (name, labels)
                else:
                    filters += '\t\t**%s**: %s\n' % (name, self.query_params.get(name))
        return filters

    def get_columns_properties(self):
        return {}

    def show_table(self):
        cols = self.get_columns_properties()
        tbl_header = [col['colname'] for col in cols]
        table_data = [tbl_header]

        for obj in self.objects:
            objs = []
            for col in cols:
                objs.append(utils.stg_get_property_value(obj, col))
            table_data.append(objs)

        objects_table = SingleTable(table_data)
        return objects_table.table

    def get_objects(self):
        return []


class StGitlabProjectIssuesListCommand(StGitlabProjectObjectsListCommand):
    shortcuts = OrderedDict([
        ('Enter', 'open'),
        ('F5', 'refresh'),
        ('Delete', 'delete'),
        ('f', 'filter'),
        ('Shift + ←', 'prev. page'),
        ('Shift + →', 'next page')
    ])

    def get_objects(self):
        return self.gitlab.issues(**self.query_params)

    def get_columns_properties(self):
        return utils.stg_get_setting('issue_list_columns', {})


class StGitlabProjectMergesListCommand(StGitlabProjectObjectsListCommand):
    shortcuts = OrderedDict([
        ('Enter', 'open'),
        ('r', 'refresh'),
        ('F5', 'filter'),
        ('Shift + ←', 'prev. page'),
        ('Shift + →', 'next page')
    ])

    def get_objects(self):
        return self.gitlab.merges(**self.query_params)

    def get_columns_properties(self):
        return utils.stg_get_setting('merge_requests_list_columns', {})


class StGitlabProjectPipelinesListCommand(StGitlabProjectObjectsListCommand):
    shortcuts = OrderedDict([
        ('Enter', 'open'),
        ('F5', 'refresh'),
        ('b', 'retry'),
        ('c', 'cancel'),
        ('f', 'filter'),
        ('Shift + ←', 'prev. page'),
        ('Shift + →', 'next page')
    ])

    def get_objects(self):
        return self.gitlab.pipelines(**self.query_params)

    def get_columns_properties(self):
        return utils.stg_get_setting('pipelines_list_columns', {})
