#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

from __future__ import annotations
from typing import TYPE_CHECKING
import sublime  # type:ignore
import sublime_plugin  # type:ignore

from . import utils
from .stg_project import ProjectSelectPanel
from .stg_object import StGitlabObjectCommand

if TYPE_CHECKING:
    from ..libs.gitlab.v4.objects import Issue  # type: ignore


# Create Issue
class StGitlabIssueCreateCommand(sublime_plugin.TextCommand):
    def run(self, edit: sublime.Edit) -> None:
        self.gitlab = utils.gl.get()
        self.project_id = self.view.settings().get("project_id", None)
        if self.project_id:
            self.set_project(self.project_id)
        else:
            panel = ProjectSelectPanel(callback=self.set_project)
            panel.show_input()

    def set_project(self, project_id: int) -> None:
        self.project_id = project_id
        self.project = self.gitlab.project(oid=self.project_id)
        self.get_issue_title()

    def get_issue_title(self) -> None:
        self.view.window().show_input_panel("New issue title:", "", self.create_issue, None, None)

    def create_issue(self, title: str) -> None:
        if not title:
            return

        if self.project is None:
            raise ValueError("Create issues error: project undefined")

        issue = self.project.issues.create({"title": title})
        r = sublime.active_window().new_file()
        r.set_scratch(True)
        syntax_file = utils.get_setting("syntax_file")
        r.set_syntax_file(syntax_file)
        r.settings().set("object_id", issue.iid)
        r.settings().set("project_id", self.project_id)
        r.run_command("st_gitlab_issue_fetcher", {"obj_id": issue.iid})


class StGitlabIssueCommand(StGitlabObjectCommand):
    INPUT_STR = "Issue ID"
    object_name = "issue"

    def get_issue(self) -> Issue:
        return self.gitlab.issue(project_id=self.project_id, oid=self.obj_id)


class StGitlabIssueDeleteCommand(StGitlabIssueCommand):
    VALID_SCREENS = {
        "issue": ["screen_view", "screen_list"],
    }

    INPUT_STR = "Issue ID to delete"

    def refresh(self) -> None:
        if self.screen == "st_gitlab_issues":
            self.view.run_command("st_gitlab_project_list_refresh")
        elif self.screen == "st_gitlab_issue":
            self.view.close()

    def process(self) -> None:
        if not self.obj_id:
            return
        is_del = sublime.ok_cancel_dialog(f"Are you really want to delete issue #{self.obj_id}?")
        if not is_del:
            return
        issue = self.get_issue()
        issue.delete()
        self.refresh()
