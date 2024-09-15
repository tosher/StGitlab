#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

from __future__ import annotations
from typing import TYPE_CHECKING

import sublime  # type: ignore

from ..libs import gitlab  # type: ignore

if TYPE_CHECKING:
    from typing import Optional, List, Dict, Any
    from ..libs.gitlab.base import RESTObject  # type: ignore
    from ..libs.gitlab.v4 import objects as GitlabObjects  # type: ignore
    from .types import ProjectId


GITLAB_API_VERSION = "4"


class StGitlabError(Exception):
    pass


class StGitlab(object):
    clabels: List[GitlabObjects.ProjectLabel] = []
    cprojects: List[GitlabObjects.Project] = []
    cproject: Dict[int, GitlabObjects.Project] = {}
    cusers: List[GitlabObjects.User] = []
    cgroups: List[GitlabObjects.Group] = []
    cgroup: Dict[str, GitlabObjects.Group] = {}

    @staticmethod
    def connect() -> gitlab.Gitlab:
        settings = sublime.load_settings("StGitlab.sublime-settings")
        url = settings.get("gitlab_url")
        api_key = settings.get("api_token")
        ssl_verify = settings.get("ssl_verify")
        return gitlab.Gitlab(url, api_key, api_version=GITLAB_API_VERSION, ssl_verify=ssl_verify)

    def __init__(self) -> None:
        self._view: Optional[sublime.View] = None
        self._conn: Optional[gitlab.Gitlab] = None

    @property
    def view(self) -> sublime.View:
        if self._view is None:
            raise StGitlabError("View is not defined")
        return self._view

    @property
    def conn(self) -> gitlab.Gitlab:
        if self._conn is None:
            raise StGitlabError("Not connected to Gitlab")
        return self._conn

    def reset(self) -> None:
        self._conn = None
        self.clabels = []
        self.cprojects = []
        self.cproject = {}
        self.cusers = []
        self.cgroups = []
        self.cgroup = {}

    def get(self, view: Optional[sublime.View] = None) -> "StGitlab":
        self._view = sublime.active_window().active_view() if view is None else view
        if not self._conn:
            self._conn = StGitlab.connect()
        return self

    def view_object_name(self) -> Optional[str]:
        return self.view.settings().get("object_name", None)

    def object_by_view(self, **kwargs: Any) -> RESTObject:
        obj_name = self.view_object_name()
        if obj_name is None:
            raise StGitlabError(f"Object name is not defined for view {self.view.id()} ({self.view.name()})")

        if hasattr(self, obj_name):
            funcobj = getattr(self, obj_name)
            return funcobj(**kwargs)

        raise StGitlabError(f"Object {obj_name} not supported by plugin")

    def project(self, oid: Optional[ProjectId] = None) -> GitlabObjects.Project:
        """
        oid - ID or name with namespace (namespace/project_name)
        """
        if oid is None:
            oid = self.view.settings().get("project_id", None)

        if not oid:
            raise StGitlabError("Project not found - id undefined")

        if isinstance(oid, int) and oid in self.cproject:
            return self.cproject[oid]

        prj = self.conn.projects.get(oid)
        if not prj:
            raise StGitlabError(f"Project with oid {oid} not found")

        self.cproject[prj.id] = self.conn.projects.get(oid)
        return prj

    def issue(self, project_id: Optional[int] = None, oid: Optional[int] = None) -> GitlabObjects.Issue:
        if oid is None:
            oid = self.view.settings().get("object_id", None)
        if not oid:
            raise StGitlabError("Issue id is not defined")
        project = self.project(project_id)
        if project is None:
            raise StGitlabError("Project not found")
        return project.issues.get(oid)

    def pipeline(self, project_id: Optional[int] = None, oid: Optional[int] = None) -> GitlabObjects.ProjectPipeline:
        if oid is None:
            oid = self.view.settings().get("object_id", None)
        if not oid:
            raise StGitlabError("Pipeline id is not defined")
        project = self.project(project_id)
        if project is None:
            raise StGitlabError("Project not found")
        return project.pipelines.get(oid)

    def merge(self, project_id: Optional[int] = None, oid: Optional[int] = None) -> GitlabObjects.ProjectMergeRequest:
        if oid is None:
            oid = self.view.settings().get("object_id", None)

        if not oid:
            raise StGitlabError("Merge-request id is not defined")

        project = self.project(project_id)
        if project is None:
            raise StGitlabError("Merge-request not found - project not defined")

        return project.mergerequests.get(oid)

    def group(self, gr: str) -> Optional[GitlabObjects.Group]:
        if gr in self.cgroup:
            return self.cgroup[gr]

        group = self.conn.groups.get(gr)
        if not group:
            return None
        self.cgroup[gr] = group
        return group

    def users(self, **kwargs: Any) -> List[GitlabObjects.User]:
        if len(kwargs.keys()) == 1 and kwargs.get("all", False):
            if not self.cusers:
                self.cusers = self.conn.users.list(**kwargs)
            return self.cusers
        else:
            return self.conn.users.list(**kwargs)

    def user(self, oid: Optional[int] = None, name: Optional[str] = None) -> GitlabObjects.User:
        if not oid and not name:
            raise StGitlabError("User id or name are not defined")

        if oid:
            return self.conn.users.get(oid)

        users = self.conn.users.list(username=name)
        if users:
            return users[0]
        else:
            raise StGitlabError('User with name "{}" does not found'.format(name))

    def assignee_set(self, oid: int, obj: RESTObject) -> None:
        obj.assignee_id = oid
        obj.save()

    def assignee_del(self, obj: RESTObject) -> None:
        # obj.assignee_id = None  # not works
        obj.assignee_ids = []
        obj.save()

    def projects(self, **kwargs: Any) -> List[GitlabObjects.Project]:
        if len(kwargs.keys()) == 1 and kwargs.get("all", False):
            if not self.cprojects:
                self.cprojects = self.conn.projects.list(**kwargs)
            return self.cprojects
        else:
            return self.conn.projects.list(**kwargs)

    def groups(self, **kwargs: Any) -> List[GitlabObjects.Group]:
        if len(kwargs.keys()) == 1 and kwargs.get("all", False):
            if not self.cgroups:
                self.cgroups = self.conn.groups.list(**kwargs)
            return self.cgroups
        else:
            return self.conn.groups.list(**kwargs)

    def issues(self, project_id: Optional[int] = None, **kwargs: Any) -> List[GitlabObjects.Issue]:
        project = self.project(project_id)
        if project is None:
            raise StGitlabError("Project not found")

        return project.issues.list(**kwargs)

    def pipelines(self, project_id: Optional[int] = None, **kwargs: Any) -> List[GitlabObjects.ProjectPipeline]:
        project = self.project(project_id)
        if project is None:
            raise StGitlabError("Project not found")

        return project.pipelines.list(**kwargs)

    def merges(self, project_id: Optional[int] = None, **kwargs: Any) -> List[GitlabObjects.ProjectMergeRequest]:
        project = self.project(project_id)
        if project is None:
            raise StGitlabError("Project not found")

        return project.mergerequests.list(**kwargs)

    def labels(self, project_id: Optional[int] = None, **kwargs: Any) -> List[GitlabObjects.ProjectLabel]:
        """
        Group labels available in project, no need to extract
        """

        project = self.project(project_id)
        if project is None:
            raise StGitlabError("Project not found")

        if len(kwargs.keys()) == 1 and kwargs.get("all", False):
            if not self.clabels:
                # self.clabels = project.labels.list(**kwargs) + group_labels
                self.clabels = project.labels.list(**kwargs)
            return self.clabels
        else:
            return project.labels.list(**kwargs)

    def label_add(self, label: str, obj: RESTObject) -> None:
        if label not in obj.labels:
            obj.labels.append(label)
        obj.save()

    def label_del(self, label: str, obj: RESTObject) -> None:
        if label in obj.labels:
            obj.labels.remove(label)
        obj.save()

    def milestones(self, project_id: Optional[int] = None, **kwargs: Any) -> List[GitlabObjects.ProjectMilestone]:
        project = self.project(project_id)
        if project is None:
            raise StGitlabError("Project not found")

        return project.milestones.list(**kwargs)

    def milestone_set(self, oid: Optional[int], obj: RESTObject) -> None:
        obj.milestone_id = oid
        obj.save()

    def milestone_del(self, obj: RESTObject) -> None:
        self.milestone_set(None, obj)

    def branch(self, project_id: Optional[int] = None, oid: Optional[int] = None) -> GitlabObjects.ProjectBranch:
        project = self.project(project_id)
        if project is None:
            raise StGitlabError("Project not found")

        return project.branches.get(oid)

    def branches(self, project_id: Optional[int] = None, **kwargs: Any) -> List[GitlabObjects.ProjectBranch]:
        project = self.project(project_id)
        if project is None:
            raise StGitlabError("Project not found")

        return project.branches.list(**kwargs)

    def jobs(self, project_id: Optional[int] = None, **kwargs: Any) -> List[GitlabObjects.ProjectJob]:
        project = self.project(project_id)
        if project is None:
            raise StGitlabError("Project not found")

        return project.jobs.list(**kwargs)

    def commits(self, project_id: Optional[int] = None, **kwargs: Any) -> List[GitlabObjects.ProjectCommit]:
        project = self.project(project_id)
        if project is None:
            raise StGitlabError("Project not found")

        return project.commits.list(**kwargs)

    def boards(self, project_id: Optional[int] = None, **kwargs: Any) -> List[GitlabObjects.ProjectBoard]:
        project = self.project(project_id)
        if project is None:
            raise StGitlabError("Project not found")

        return project.boards.list(**kwargs)

    def commit(self, sha: str, project_id: Optional[int] = None) -> GitlabObjects.ProjectCommit:
        project = self.project(project_id)
        if project is None:
            raise StGitlabError("Project not found")

        return project.commits.get(sha)

    def snippets(self, project_id: Optional[int] = None, **kwargs: Any) -> List[GitlabObjects.Snippet]:
        if project_id:
            project = self.project(project_id)
            if project is None:
                raise StGitlabError("Project not found")
            return project.snippets.list(**kwargs)

        return self.conn.snippets.list(**kwargs)

    def snippet(self, project_id: Optional[int] = None, oid: Optional[int] = None) -> GitlabObjects.Snippet:
        if oid is None:
            oid = self.view.settings().get("object_id", None)
        if not oid:
            raise StGitlabError("Snippet id is not defined")

        if project_id:
            project = self.project(project_id)
            if project is None:
                raise StGitlabError("Project not found")
            return project.snippets.get(oid)

        return self.conn.snippets.get(oid)
