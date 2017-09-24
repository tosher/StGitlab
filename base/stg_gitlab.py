#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

import sys
import os
import sublime
sys.path.append(os.path.join(os.path.dirname(__file__), "../libs"))
import gitlab

# TODO: request use for ssl validation
# requests = settings.get('connection_options')


class StGitlab(object):
    def connect():
        settings = sublime.load_settings("StGitlab.sublime-settings")
        url = settings.get('gitlab_url')
        api_key = settings.get('api_token')
        return gitlab.Gitlab(url, api_key, api_version=4)

    def __init__(self):
        self.connect = StGitlab.connect()
        self.view = sublime.active_window().active_view()

    def object_name_by_screen(self, screen):
        return screen.split('_')[-1]

    def object_by_screen(self, screen, **kwargs):
        obj_name = self.object_name_by_screen(screen)
        if hasattr(self, obj_name):
            funcobj = getattr(self, obj_name)
            return funcobj(**kwargs)
        return None

    def project(self, oid=None):
        if oid is None:
            oid = self.view.settings().get('project_id', None)
        if not oid:
            raise Exception('Project id is not defined')
        return self.connect.projects.get(oid)

    def issue(self, project_id=None, oid=None):
        if oid is None:
            oid = self.view.settings().get('object_id', None)
        if not oid:
            raise Exception('Issue id is not defined')
        return self.project(project_id).issues.get(oid)

    def pipeline(self, project_id=None, oid=None):
        if oid is None:
            oid = self.view.settings().get('object_id', None)
        if not oid:
            raise Exception('Pipeline id is not defined')
        return self.project(project_id).pipelines.get(oid)

    def merge(self, project_id=None, oid=None):
        if oid is None:
            oid = self.view.settings().get('object_id', None)
        if not oid:
            raise Exception('Merge-request id is not defined')
        return self.project(project_id).mergerequests.get(oid)

    def group(self, gr):
        return self.connect.groups.get(gr)

    def users(self, **kwargs):
        return self.connect.users.list(**kwargs)

    def projects(self, **kwargs):
        return self.connect.projects.list(**kwargs)

    def groups(self, **kwargs):
        return self.connect.groups.list(**kwargs)

    def issues(self, project_id=None, **kwargs):
        return self.project(project_id).issues.list(**kwargs)

    def pipelines(self, project_id=None, **kwargs):
        return self.project(project_id).pipelines.list(**kwargs)

    def merges(self, project_id=None, **kwargs):
        return self.project(project_id).mergerequests.list(**kwargs)

    def labels(self, project_id=None, **kwargs):
        return self.project(project_id).labels.list(**kwargs)

    def milestones(self, project_id=None, **kwargs):
        return self.project(project_id).milestones.list(**kwargs)

