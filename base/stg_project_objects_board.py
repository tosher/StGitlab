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


class StGitlabProjectIssuesBoardDrawCommand(sublime_plugin.TextCommand):

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

    def run(self, edit, title):
        self.title = title
        self.query_params = self.view.settings().get('query_params', {})
        self.gitlab = utils.gl.get()
        self.board = self.get_board()
        self.labels = self.gitlab.labels(all=True)
        self.labels_backlog = self.get_backlog_labels()
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
        # header += '\t**Total**: %s\n' % len(self.objects)
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

    def get_board(self):
        return self.gitlab.boards()[0]

    def get_backlog_labels(self):
        lists_labels = []
        lists = self.board.attributes.get('lists', [])
        for li in lists:
            lists_labels.append(self.list_label(li))
        return [l.name for l in self.labels if l.name not in lists_labels]

    def get_issues_backlog(self):
        blabels = self.get_backlog_labels()
        issues = []
        for lab in blabels:
            issues += self.gitlab.issues(labels=[lab], state='opened')
        return list(set(issues))

    def get_issues_closed(self):
        return self.gitlab.issues(state='closed')

    def get_issues_list(self, li):
        return self.gitlab.issues(labels=[self.list_label(li)], state='opened')

    def list_label(self, li):
        return li.get('label', {}).get('name')

    # def get_columns_properties(self):
    #     return utils.stg_get_setting('issue_list_columns', {})

    # TODO: issue with important & in_progress: which list?
    def show_table(self):
        max_width = 35
        tbl_header = ['Backlog'] + [self.list_label(li) for li in self.board.attributes.get('lists', [])] + ['Closed']
        table_data = [tbl_header]

        by_cols = []
        by_cols.append(self.get_issues_backlog())
        for li in self.board.attributes.get('lists', []):
            li_issues = self.get_issues_list(li)
            by_cols.append(li_issues)
        by_cols.append(self.get_issues_closed())

        lines_cnt = len(max(by_cols, key=len))
        for linenum in range(lines_cnt):
            table_line = []
            for col in by_cols:
                if len(col) >= linenum + 1:
                    issue_str = '%s: %s' % (col[linenum].iid, col[linenum].title)
                    table_line.append(utils.stg_cut(issue_str, max_width))
                else:
                    table_line.append('')
            table_data.append(table_line)

        objects_table = SingleTable(table_data)
        return objects_table.table
