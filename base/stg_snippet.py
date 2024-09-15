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
    from typing import Optional
    from ..libs.gitlab.v4.objects import Project  # type: ignore


class StGitlabSnippetCreateCommand(sublime_plugin.TextCommand):
    visibility = ["private", "internal", "public"]

    def run(self, edit: sublime.Edit) -> None:
        self.gitlab = utils.gl.get()
        self.project: Optional[Project] = None
        self.project_id = self.view.settings().get("project_id", None)
        if self.project_id:
            self.set_project(self.project_id)
        else:
            panel = ProjectSelectPanel(callback=self.set_project, required=False)
            panel.show_input()

    def set_project(self, project_id: int) -> None:
        self.project_id = project_id
        if self.project_id:
            self.project = self.gitlab.project(oid=self.project_id)
        self.get_snippet_title()

    def get_snippet_title(self) -> None:
        self.view.window().show_input_panel("New snippet title:", "", self.get_snippet_file, None, None)

    def get_snippet_file(self, title: str) -> None:
        if not title:
            return
        self.title = title
        self.view.window().show_input_panel("Snippet file name (for syntax highlight):", "", self.get_visibility, None, None)

    def get_visibility(self, file_name: str) -> None:
        if not file_name:
            return
        self.file_name = file_name
        self.view.window().show_quick_panel(self.visibility, self.create_snippet)

    def create_snippet(self, visibility_idx: int) -> None:
        if visibility_idx < 0:
            return

        visibility_value = self.visibility[visibility_idx]
        create_method = self.gitlab.conn.snippets.create if self.project is None else self.project.snippets.create
        snippet = create_method(
            {"title": self.title, "file_name": self.file_name, "content": "-", "code": "-", "visibility": visibility_value}
        )
        r = sublime.active_window().new_file()
        r.set_scratch(True)
        syntax_file = utils.get_setting("syntax_file")
        r.set_syntax_file(syntax_file)
        r.settings().set("object_id", snippet.id)
        if self.project:
            r.settings().set("project_id", self.project_id)
        r.run_command("st_gitlab_snippet_fetcher", {"obj_id": snippet.id})


class StGitlabSnippetCommand(StGitlabObjectCommand):
    INPUT_STR = "Snippet ID"
    object_name = "snippet"
    project_required = False

    # def get_issue(self):
    #     return self.gitlab.snippet(project_id=self.project_id, oid=self.obj_id)


class StGitlabSnippetDeleteCommand(StGitlabSnippetCommand):
    VALID_SCREENS = {
        "snippet": ["screen_view", "screen_list"],
    }

    INPUT_STR = "Snippet ID to delete"

    def refresh(self) -> None:
        if self.screen == "st_gitlab_snippets":
            self.view.run_command("st_gitlab_project_list_refresh")
        elif self.screen == "st_gitlab_snippet":
            self.view.close()

    def process(self) -> None:
        if not self.obj_id:
            return
        is_del = sublime.ok_cancel_dialog(f"Are you really want to delete snippet #{self.obj_id}?")
        if not is_del:
            return
        snippet = self.get_snippet()
        snippet.delete()
        self.refresh()
