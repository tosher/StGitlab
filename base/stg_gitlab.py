#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

import sys
import os
import sublime
sys.path.append(os.path.join(os.path.dirname(__file__), "../libs"))
from ..libs import gitlab


class StGitlab(object):

    conn = None
    view = None
    clabels = None
    cprojects = None
    cproject = {}
    cusers = None
    cgroups = None
    cgroup = {}

    @staticmethod
    def connect():
        settings = sublime.load_settings("StGitlab.sublime-settings")
        url = settings.get('gitlab_url')
        api_key = settings.get('api_token')
        ssl_verify = settings.get('ssl_verify')
        return gitlab.Gitlab(url, api_key, api_version=4, ssl_verify=ssl_verify)

    def __init__(self):
        pass

    def reset(self):
        self.conn = None
        self.clabels = None
        self.cprojects = None
        self.cproject = {}
        self.cusers = None
        self.cgroups = None
        self.cgroup = {}

    def get(self, view=None):
        self.view = sublime.active_window().active_view() if view is None else view
        if not self.conn:
            self.conn = StGitlab.connect()
        return self

    def view_object_name(self):
        return self.view.settings().get('object_name', None)

    def object_by_view(self, **kwargs):
        obj_name = self.view_object_name()
        if obj_name is None:
            raise Exception('Object name is not defined for view %s (%s)' % (self.view.id(), self.view.name()))
        if hasattr(self, obj_name):
            funcobj = getattr(self, obj_name)
            return funcobj(**kwargs)
        return None

    def project(self, oid=None):
        if oid is None:
            oid = self.view.settings().get('project_id', None)
        if not oid:
            # raise Exception('Project id is not defined')
            return None
        if not self.cproject.get(oid):
            self.cproject[oid] = self.conn.projects.get(oid)
        return self.cproject.get(oid)

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
        if not self.cgroup.get(gr):
            self.cgroup[gr] = self.conn.groups.get(gr)
        return self.cgroup.get(gr)

    def users(self, **kwargs):
        if len(kwargs.keys()) == 1 and kwargs.get('all', False):
            if not self.cusers:
                self.cusers = self.conn.users.list(**kwargs)
            return self.cusers
        else:
            return self.conn.users.list(**kwargs)

    def user(self, oid=None):
        if oid is None:
            raise Exception('User id is not defined')
        return self.conn.users.get(oid)

    def assignee_set(self, oid, obj):
        obj.assignee_id = oid
        obj.save()

    def assignee_del(self, obj):
        # obj.assignee_id = None  # not works
        obj.assignee_ids = []
        obj.save()

    def projects(self, **kwargs):
        if len(kwargs.keys()) == 1 and kwargs.get('all', False):
            if not self.cprojects:
                self.cprojects = self.conn.projects.list(**kwargs)
            return self.cprojects
        else:
            return self.conn.projects.list(**kwargs)

    def groups(self, **kwargs):
        if len(kwargs.keys()) == 1 and kwargs.get('all', False):
            if not self.cgroups:
                self.cgroups = self.conn.groups.list(**kwargs)
            return self.cgroups
        else:
            return self.conn.groups.list(**kwargs)

    def issues(self, project_id=None, **kwargs):
        return self.project(project_id).issues.list(**kwargs)

    def pipelines(self, project_id=None, **kwargs):
        return self.project(project_id).pipelines.list(**kwargs)

    def merges(self, project_id=None, **kwargs):
        return self.project(project_id).mergerequests.list(**kwargs)

    def labels(self, project_id=None, **kwargs):
        if not project_id:
            # NOTE: example: global snippet (no project)
            return []
        if len(kwargs.keys()) == 1 and kwargs.get('all', False):
            if not self.clabels:
                self.clabels = self.project(project_id).labels.list(**kwargs)
            return self.clabels
        else:
            return self.project(project_id).labels.list(**kwargs)

    def label_add(self, label, obj):
        if label not in obj.labels:
            obj.labels.append(label)
        obj.save()

    def label_del(self, label, obj):
        if label in obj.labels:
            obj.labels.remove(label)
        obj.save()

    def milestones(self, project_id=None, **kwargs):
        return self.project(project_id).milestones.list(**kwargs)

    def milestone_set(self, oid, obj):
        obj.milestone_id = oid
        obj.save()

    def milestone_del(self, obj):
        self.milestone_set(None, obj)

    def branch(self, project_id=None, oid=None):
        return self.project(project_id).branches.get(oid)

    def branches(self, project_id=None, **kwargs):
        return self.project(project_id).branches.list(**kwargs)

    def jobs(self, project_id=None, **kwargs):
        return self.project(project_id).jobs.list(**kwargs)

    def commits(self, project_id=None, **kwargs):
        return self.project(project_id).commits.list(**kwargs)

    def boards(self, project_id=None, **kwargs):
        return self.project(project_id).boards.list(**kwargs)

    def commit(self, sha, project_id=None):
        return self.project(project_id).commits.get(sha)

    def snippets(self, project_id=None, **kwargs):
        obj = self.project(project_id) if project_id else self.conn
        return obj.snippets.list(**kwargs)

    def snippet(self, project_id=None, oid=None):
        if oid is None:
            oid = self.view.settings().get('object_id', None)
        if not oid:
            raise Exception('Snippet id is not defined')
        if project_id:
            return self.project(project_id).snippets.get(oid)
        return self.conn.snippets.get(oid)
