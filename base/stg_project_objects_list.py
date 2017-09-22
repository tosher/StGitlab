#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

import sys
import os
import sublime
import sublime_plugin
from collections import OrderedDict
from .stg_gitlab import StGitlab
from . import stg_utils as utils
sys.path.append(os.path.join(os.path.dirname(__file__), "../libs"))
from terminaltables.other_tables import WindowsTable as SingleTable


class StGitlabProjectObjectsListCommand(sublime_plugin.TextCommand):

    html_tpl = '''
    <html>
        <style>
            tt.kbd {
                color: #C5C2A2;
                background-color: #555555;
                font-size: 1rem;
                border-radius: 0.6rem;
                padding: 0.2rem;
                padding-left: 0.4rem;
                padding-right: 0.4rem;
            }

            span.keyname {
                color: #c0c0c0;
                font-size: 1rem;
                padding: 0.2rem;
                padding-left: 0.3rem;
                padding-right: 0.4rem;
            }
        </style>
        <body id="gitlab" style="padding:0;margin:0;">
        %(shortcuts)s
        </body>
    </html>
    '''

    html_shortcut_tpl = '<tt class="kbd">%(keyname)s</tt><span class="keyname">%(cmdname)s</span>'

    shortcuts = {}

    def run(self, edit, title):
        self.title = title
        self.gitlab = StGitlab.connect()
        self.project_id = self.view.settings().get('project_id')
        self.project = self.gitlab.projects.get(self.project_id)
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

    def show_shortcuts(self):
        if not self.shortcuts:
            return
        shortcuts_html = '\n'.join(
            [
                self.html_shortcut_tpl % {'keyname': keyname, 'cmdname': self.shortcuts[keyname]} for keyname in self.shortcuts.keys()
            ]
        )

        shortcuts_menu_html = self.html_tpl % {'shortcuts': shortcuts_html}
        self.view.add_phantom(
            'shortcuts',
            sublime.Region(0, 0),
            shortcuts_menu_html,
            sublime.LAYOUT_INLINE
        )

    def show_header(self):
        header = '\n\n'
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
                    labels = ', '.join(['^%s^' % label for label in self.query_params.get(name)])
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
        ('r', 'refresh'),
        ('Delete', 'delete'),
        ('f', 'filter'),
        ('Shift + ←', 'prev. page'),
        ('Shift + →', 'next page')
    ])

    def get_objects(self):
        return self.project.issues.list(**self.query_params)

    def get_columns_properties(self):
        return utils.stg_get_setting('issue_list_columns', {})


class StGitlabProjectMergesListCommand(StGitlabProjectObjectsListCommand):
    shortcuts = OrderedDict([
        ('Enter', 'open'),
        ('r', 'refresh'),
        ('f', 'filter'),
        ('Shift + ←', 'prev. page'),
        ('Shift + →', 'next page')
    ])

    def get_objects(self):
        return self.project.mergerequests.list(**self.query_params)

    def get_columns_properties(self):
        return utils.stg_get_setting('merge_requests_list_columns', {})


class StGitlabProjectPipelinesListCommand(StGitlabProjectObjectsListCommand):
    shortcuts = OrderedDict([
        ('Enter', 'open'),
        ('r', 'refresh'),
        ('b', 'retry'),
        ('c', 'cancel'),
        ('f', 'filter'),
        ('Shift + ←', 'prev. page'),
        ('Shift + →', 'next page')
    ])

    def get_objects(self):
        return self.project.pipelines.list(**self.query_params)

    def get_columns_properties(self):
        return utils.stg_get_setting('pipelines_list_columns', {})
