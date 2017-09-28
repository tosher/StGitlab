#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

import sys
import os
# import sublime
import sublime_plugin
from . import stg_utils as utils

class StGitlabProjectObjectsListActionCommand(sublime_plugin.TextCommand):
    valid_actions = [
        'set_label',
        'del_label',
        'set_milestone',
        'del_milestone'
    ]

    def run(self, edit, action):
        self.action = action
        self.gitlab = utils.gl.get()
        colsep = utils.stg_get_setting('table_column_separator')
        self.view.set_read_only(False)
        selection = self.view.sel()
        obj_ids = []
        for sel in self.view.lines(selection[0]):
            line = self.view.substr(self.view.line(sel.end()))
            obj_id = line.split(colsep)[1].strip()
            obj_ids.append(obj_id)

        if self.action in self.valid_actions:
            funcobj = getattr(self, self.action)
            funcobj(obj_ids)

    def get_label(self, on_done):
        screen = self.view.settings().get('screen', None)
        labels = self.gitlab.labels(all=True)
        labels_names = [lab.name for lab in labels]
        if screen == 'st_gitlab_issues':
            object_name = 'issue'
        elif screen == 'st_gitlab_merges':
            object_name = 'merge'
        self.view.window().show_quick_panel(labels_names, on_done)

    def set_label(self, obj_ids):
        self.process_label(obj_ids)

    def del_label(self, obj_ids):
        self.process_label(obj_ids)

    def process_label(self, obj_ids):
        def on_done(i):
            if self.action == 'set_label':
                set_label(i)
            elif self.action == 'del_label':
                del_label(i)

        def set_label(i):
            if i < 0:
                return
            for obj_id in obj_ids:
                obj = self.gitlab.object_by_screen(object_name, oid=obj_id)
                obj_labels = obj.attributes.get('labels', [])
                if not labels_names[i] in obj_labels:
                    obj_labels.append(labels_names[i])
                obj.save(labels=','.join(obj_labels))
            self.view.run_command('st_gitlab_project_list_refresh')


        def del_label(i):
            if i < 0:
                return
            for obj_id in obj_ids:
                if screen == 'st_gitlab_issues':
                    obj = self.gitlab.issue(oid=obj_id)
                elif screen == 'st_gitlab_merges':
                    obj = self.gitlab.merge(oid=obj_id)
                obj_labels = obj.attributes.get('labels', [])
                if labels_names[i] in obj_labels:
                    obj_labels.remove(labels_names[i])
                obj.save(labels=','.join(obj_labels))
            self.view.run_command('st_gitlab_project_list_refresh')

        screen = self.view.settings().get('screen', None)
        labels = self.gitlab.labels(all=True)
        labels_names = [lab.name for lab in labels]
        if screen == 'st_gitlab_issues':
            object_name = 'issue'
        elif screen == 'st_gitlab_merges':
            object_name = 'merge'
        self.view.window().show_quick_panel(labels_names, on_done)
