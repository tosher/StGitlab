#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

from __future__ import annotations
from typing import TYPE_CHECKING

import re
import webbrowser
import sublime  # type:ignore

from . import utils
from .stg_object import StGitlabObjectTextCommand

if TYPE_CHECKING:
    from typing import Optional
    from ..libs.gitlab.v4.objects import Project  # type: ignore
    from .stg_gitlab import StGitlab


class StGitlabUtilOpenUrlCommand(StGitlabObjectTextCommand):
    VALID_SCREENS = {
        "issue": ["screen_view"],
        "merge": ["screen_view"],
    }

    @property
    def gitlab(self) -> StGitlab:
        if self._gitlab is None:
            raise ValueError("Gitlab not connected")

        return self._gitlab

    @property
    def project(self) -> Project:
        if self._project is None:
            raise ValueError("Project is undefined")

        return self._project

    def _get_markdown_url(self, text: str) -> Optional[str]:
        url = None

        if not re.findall(r"\]\((.*?)\)", text):
            return None

        try:
            url = self.view.substr(self.view.sel()[0]).split("(")[1].split(")")[0]
            if not url:
                return None

            if not url.startswith("http"):
                project_name = self.project.attributes.get("path_with_namespace")
                gl_url = utils.get_setting("gitlab_url").rstrip("/")
                url = f"{gl_url}/{project_name}/{url.lstrip('/')}"

        except Exception as e:
            sublime.active_window().status_message(f"Unable to open Url: {e}")
            return None

        return url

    def _get_native_url(self, text: str) -> Optional[str]:
        try:
            urls = re.findall(
                r"(https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*))",
                text,
            )
        except Exception as e:
            sublime.active_window().status_message(f"Unable to open Url: {e}")
            return None

        if not urls:
            return None

        return urls[0][0]

    def _open_linked_issue(self, text: str) -> bool:
        issues = re.findall(r"([/\w]+)?\#(\d+)", text)
        if not issues:
            return False

        for iss in issues:
            print(iss)

        project_path, issue_id = issues[0]
        project_id = self.project.id
        if project_path:
            # Link to issue in another project
            if "/" in project_path:
                # Project in other namespace
                # > 111: ... marked this issue as related to grp28/prjfoo#77 (11.09.2021 12:06:15)
                project_go = self.gitlab.project(oid=project_path)
            else:
                # The same namespace as current project
                # > 111: ... marked this issue as related to prjtest#17 (11.09.2021 12:06:15)
                namespace = self.project.namespace.get("path", "")
                project_go = self.gitlab.project(oid=f"{namespace}/{project_path}")

            if project_go is None:
                return False

            project_id = project_go.id

        self.view.run_command("st_gitlab_issue_fetcher", {"obj_id": issue_id, "project_id": project_id})
        return True

    def _open_linked_merge(self, text: str) -> bool:
        merges = re.findall(r"([/\w]+)?\!(\d+)", text)
        if not merges:
            return False

        project_path, merge_id = merges[0]
        project_id = None
        if project_path:
            if "/" in project_path:
                project_go = self.gitlab.project(oid=project_path)
            else:
                namespace = self.project.namespace.get("path", "")
                project_go = self.gitlab.project(oid=f"{namespace}/{project_path}")

            if project_go is None:
                return False

            project_id = project_go.id
        self.view.run_command("st_gitlab_merge_fetcher", {"obj_id": merge_id, "project_id": project_id})
        return True

    def run(self, edit: sublime.Edit) -> None:
        self._gitlab = utils.gl.get()
        self._project = self.gitlab.project()

        text = self.view.substr(self.view.sel()[0])

        url = self._get_markdown_url(text)
        if url:
            webbrowser.open(url)
            return

        url = self._get_native_url(text)
        if url:
            webbrowser.open(url)
            return

        ok = self._open_linked_issue(text)
        if ok:
            return

        self._open_linked_merge(text)
