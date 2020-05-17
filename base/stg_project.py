#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

import sublime
# import sublime_plugin
from . import utils


class ProjectSelectPanel(object):

    def __init__(self, callback=None, required=True):
        self.callback = callback
        self.required = required
        self.window = sublime.active_window()

    def show_input(self):
        projects_menu = ['All projects', 'Custom']

        self.projects_filter = utils.get_setting('projects_filter', [])

        if self.projects_filter:
            projects_menu[0] = 'All projects (filtered)'

        if not self.required:
            projects_menu.append('No project')

        self.window.show_quick_panel(projects_menu, self.get_project)

    def get_project(self, idx):
        gitlab = utils.gl.get()
        if idx < 0:
            return

        if idx == 0:

            if self.projects_filter:
                projects = [gitlab.project(oid=pid) for pid in self.projects_filter]
            else:
                projects = gitlab.projects(all=True)
            self.set_project(projects)

        elif idx == 1:
            self.window.show_input_panel("Project:", '', self.get_custom_project_done, None, None)
        elif idx == 2:
            sublime.set_timeout_async(self.callback(None), 0)

    def get_custom_project_done(self, project):
        gitlab = utils.gl.get()
        projects = [gitlab.project(oid=project)]
        self.set_project(projects)

    def set_project(self, projects):
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
