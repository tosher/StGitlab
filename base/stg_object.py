#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

# import sublime
import sublime_plugin
from . import stg_utils as utils
from .stg_gitlab import StGitlab
from .stg_project import ProjectSelectPanel


class StGitlabObjectCommand(sublime_plugin.TextCommand):

    INPUT_STR = 'Object ID'
    SCREEN_LIST = ''
    SCREEN_VIEW = ''
    FETCHER = ''

    def run(self, edit, obj_id=None):
        self.obj_id = obj_id
        self.gitlab = StGitlab()
        self.get_project_id()

    def get_obj_id(self):
        if self.obj_id:
            return
        self.screen = self.view.settings().get('screen', None)
        if self.screen == self.SCREEN_LIST:
            colsep = utils.stg_get_setting('table_column_separator')
            try:
                line = self.view.substr(self.view.line(self.view.sel()[0].end()))
                self.obj_id = line.split(colsep)[1].strip()
                int(self.obj_id)
            except Exception:
                pass
        elif self.screen == self.SCREEN_VIEW:
            self.obj_id = self.view.settings().get('object_id', None)

        if not self.obj_id:
            self.view.window().show_input_panel(self.INPUT_STR, '', self.obj_done, None, None)
        else:
            self.obj_done(self.obj_id)

    def obj_done(self, obj_id):
        self.obj_id = obj_id
        self.process()

    def get_project_id(self):
        project_id = self.view.settings().get('project_id', None)
        if project_id:
            self.project_done(project_id)
        else:
            panel = ProjectSelectPanel(callback=self.project_done)
            panel.show_input()

    def project_done(self, project_id):
        self.project_id = project_id
        self.get_obj_id()

    def process(self):
        if not self.obj_id:
            return
        self.view.run_command(self.FETCHER, {'project_id': self.project_id, 'obj_id': self.obj_id})
