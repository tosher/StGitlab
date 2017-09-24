#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

import sublime
# import sublime_plugin
from . import stg_utils as utils
from .stg_gitlab import StGitlab


class ProjectSelectPanel(object):

    def __init__(self, callback=None):
        self.callback = callback
        self.window = sublime.active_window()

    def show_input(self):
        gitlab = StGitlab()
        projects_filter = utils.stg_get_setting('projects_filter', [])
        if projects_filter:
            projects = [gitlab.project(oid=pid) for pid in projects_filter]
        else:
            projects = gitlab.projects(all=True)

        self.prj_names = []
        self.prj_ids = []
        for prj in projects:
            self.prj_names.append(prj.name)
            self.prj_ids.append(prj.id)

        if len(projects) == 1:
            self.on_done(0)
        else:
            self.window.show_quick_panel(self.prj_names, self.on_done)

    def on_done(self, idx):
        if idx < 0:
            return
        project_id = self.prj_ids[idx]
        sublime.set_timeout_async(self.callback(project_id), 0)
