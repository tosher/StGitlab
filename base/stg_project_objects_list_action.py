#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

# import sublime
import sublime_plugin
from . import stg_utils as utils
from .stg_user import UserSelectPanel


class StGitlabProjectObjectsListActionCommand(sublime_plugin.TextCommand):
    valid_actions = [
        'add_label',
        'del_label',
        'set_milestone',
        'del_milestone',
        'set_assignee',
        'del_assignee'
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

    def add_label(self, obj_ids):
        self.process_label(obj_ids)

    def del_label(self, obj_ids):
        self.process_label(obj_ids)

    def process_label(self, obj_ids):
        def on_done(i):
            if i < 0:
                return
            for obj_id in obj_ids:
                obj = self.gitlab.object_by_view(oid=obj_id)
                if self.action == 'add_label':
                    self.gitlab.label_add(labels_names[i], obj)
                elif self.action == 'del_label':
                    self.gitlab.label_del(labels_names[i], obj)
            self.view.run_command('st_gitlab_project_list_refresh')

        labels = self.gitlab.labels(all=True)
        labels_names = [lab.name for lab in labels]
        self.view.window().show_quick_panel(labels_names, on_done)

    def set_milestone(self, obj_ids):
        self.process_milestone(obj_ids)

    def del_milestone(self, obj_ids):
        self.process_milestone(obj_ids)

    def process_milestone(self, obj_ids):
        def on_done(i):
            if i < 0:
                return
            for obj_id in obj_ids:
                obj = self.gitlab.object_by_view(oid=obj_id)
                if self.action == 'set_milestone':
                    self.gitlab.milestone_set(milestones[i].id, obj)
                elif self.action == 'del_milestone':
                    self.gitlab.milestone_del(obj)
            self.view.run_command('st_gitlab_project_list_refresh')

        milestones = self.gitlab.milestones(state='active')
        mile_names = [mile.title for mile in milestones]
        if self.action == 'del_milestone':
            on_done(0)
        else:
            self.view.window().show_quick_panel(mile_names, on_done)

    def set_assignee(self, obj_ids):
        self.process_assignee(obj_ids)

    def del_assignee(self, obj_ids):
        self.process_assignee(obj_ids)

    def process_assignee(self, obj_ids):
        def on_done(i):
            if i < 0:
                return
            for obj_id in obj_ids:
                obj = self.gitlab.object_by_view(oid=obj_id)
                if self.action == 'set_assignee':
                    self.gitlab.assignee_set(i, obj)
                elif self.action == 'del_assignee':
                    self.gitlab.assignee_del(obj)
            self.view.run_command('st_gitlab_project_list_refresh')

        if self.action == 'del_assignee':
            on_done(0)
        else:
            panel = UserSelectPanel(callback=on_done)
            panel.show_input()

    def is_visible(self, *args):
        screen = self.view.settings().get('screen')
        if not screen:
            return False
        valid_screens = [
            utils.object_commands.get('issue', {}).get('screen_list'),
            utils.object_commands.get('merge', {}).get('screen_list')
        ]
        if screen in valid_screens:
            return True
        return False

