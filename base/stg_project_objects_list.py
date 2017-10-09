#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

import sys
import os
from datetime import datetime, timedelta
# import sublime
import sublime_plugin
from collections import OrderedDict
from . import stg_utils as utils
from .stg_html import StShortcutsMenu
sys.path.append(os.path.join(os.path.dirname(__file__), "../libs"))
from terminaltables.other_tables import WindowsTable as SingleTable


class StGitlabProjectObjectsListCommand(sublime_plugin.TextCommand):

    shortcuts = {}
    cols = None

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
        StShortcutsMenu(self.view, shortcuts=self.shortcuts, cols=self.cols)

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
        cols_special = self.special_cols()

        for obj in self.objects:
            objs = []
            for col in cols:
                if col.get('special', False):
                    objs.append(cols_special.get(getattr(obj, col['key']), {}).get(col['prop'], ''))
                else:
                    objs.append(utils.stg_get_property_value(obj, col))
            table_data.append(objs)

        objects_table = SingleTable(table_data)
        return objects_table.table

    def get_objects(self):
        return []

    def special_cols(self):
        return {}


class StGitlabProjectIssuesListCommand(StGitlabProjectObjectsListCommand):
    shortcuts = OrderedDict([
        ('new', ['n', 'new']),
        ('open', ['Enter', 'open']),
        ('refresh', ['F5', 'refresh']),
        ('delete', ['Delete', 'delete']),
        ('filter', ['f', 'filter']),
        ('labeladd', ['l', 'add label']),
        ('labeldel', ['Alt+l', 'delete label']),
        ('mileset', ['m', 'set milestone']),
        ('miledel', ['Alt+m', 'unset milestone']),
        ('assigneeset', ['a', 'set assignee']),
        ('assigneedel', ['Alt+a', 'unset assignee']),
        ('ppage', ['Shift+%s' % utils.stg_get_setting('char_left_arrow'), 'prev. page']),
        ('npage', ['Shift+%s' % utils.stg_get_setting('char_right_arrow'), 'next page'])
    ])

    cols = [
        ['refresh', 'new', 'filter'],
        ['labeladd', 'mileset', 'assigneeset'],
        ['labeldel', 'miledel', 'assigneedel'],
        ['open', 'delete'],
        ['ppage', 'npage']
    ]

    def get_objects(self):
        return self.gitlab.issues(**self.query_params)

    def get_columns_properties(self):
        return utils.stg_get_setting('issue_list_columns', {})


class StGitlabProjectMergesListCommand(StGitlabProjectObjectsListCommand):
    shortcuts = OrderedDict([
        ('new', ['n', 'new']),
        ('open', ['Enter', 'open']),
        ('refresh', ['F5', 'refresh']),
        ('delete', ['Delete', 'delete']),
        ('filter', ['f', 'filter']),
        ('labeladd', ['l', 'add label']),
        ('labeldel', ['Alt+l', 'delete label']),
        ('mileset', ['m', 'set milestone']),
        ('miledel', ['Alt+m', 'unset milestone']),
        ('assigneeset', ['a', 'set assignee']),
        ('assigneedel', ['Alt+a', 'unset assignee']),
        ('ppage', ['Shift+%s' % utils.stg_get_setting('char_left_arrow'), 'prev. page']),
        ('npage', ['Shift+%s' % utils.stg_get_setting('char_right_arrow'), 'next page'])
    ])

    cols = [
        ['open', 'refresh', 'new'],
        ['labeladd', 'mileset', 'assigneeset'],
        ['labeldel', 'miledel', 'assigneedel'],
        ['filter', 'ppage', 'npage']
    ]

    def get_objects(self):
        return self.gitlab.merges(**self.query_params)

    def get_columns_properties(self):
        return utils.stg_get_setting('merge_requests_list_columns', {})


class StGitlabProjectPipelinesListCommand(StGitlabProjectObjectsListCommand):
    shortcuts = OrderedDict([
        ('open', ['Enter', 'open']),
        ('refresh', ['F5', 'refresh']),
        ('retry', ['b', 'retry']),
        ('cancel', ['c', 'cancel']),
        ('filter', ['f', 'filter']),
        ('ppage', ['Shift+%s' % utils.stg_get_setting('char_left_arrow'), 'prev. page']),
        ('npage', ['Shift+%s' % utils.stg_get_setting('char_right_arrow'), 'next page'])
    ])

    cols = [
        ['open'],
        ['refresh', 'filter'],
        ['retry', 'cancel'],
        ['ppage', 'npage']
    ]

    def get_objects(self):
        return self.gitlab.pipelines(**self.query_params)

    def get_columns_properties(self):
        return utils.stg_get_setting('pipelines_list_columns', {})


class StGitlabProjectBranchesListCommand(StGitlabProjectObjectsListCommand):
    shortcuts = OrderedDict([
        ('refresh', ['F5', 'refresh']),
        ('merge', ['m', 'merge-request']),
        ('toggleprotect', ['p', 'toggle protect']),
        ('filter', ['f', 'filter']),
        ('ppage', ['Shift+%s' % utils.stg_get_setting('char_left_arrow'), 'prev. page']),
        ('npage', ['Shift+%s' % utils.stg_get_setting('char_right_arrow'), 'next page'])
    ])

    cols = [
        ['refresh', 'filter'],
        ['merge', 'toggleprotect'],
        ['ppage', 'npage']
    ]

    def get_objects(self):
        return self.gitlab.branches(**self.query_params)

    def get_columns_properties(self):
        return utils.stg_get_setting('branches_list_columns', {})

    def special_cols(self):
        def diff(master, flomaster):
            master = set(master)
            flomaster_ids = [c.id for c in flomaster]
            return [item.id for item in master if item.id not in flomaster_ids]

        COMMITS_PERIOD_WEEKS = 2 * 4  # diff commits for 2 month
        cols = {}
        project = self.gitlab.project()
        since_date = (datetime.now() - timedelta(weeks=COMMITS_PERIOD_WEEKS)).strftime('%Y-%m-%dT%H:%M:%SZ')
        commits_master = project.commits.list(ref_name='master')
        for branch in self.objects:
            cols[branch.name] = {}
            if branch.name == 'master':
                cols[branch.name]['behind'] = 0
                cols[branch.name]['ahead'] = 0
                cols[branch.name]['commits_summary'] = ''
            else:
                commits = project.commits.list(ref_name=branch.name, since=since_date)
                behind = diff(commits_master, commits)
                ahead = diff(commits, commits_master)
                cols[branch.name]['behind'] = len(behind)
                cols[branch.name]['ahead'] = len(ahead)
                cols[branch.name]['commits_summary'] = 'Behind: %s, Ahead: %s' % (len(behind), len(ahead))
        return cols
