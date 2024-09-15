#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

from __future__ import annotations
from typing import TYPE_CHECKING

import sublime_plugin  # type:ignore
from . import utils
from .stg_project import ProjectSelectPanel

if TYPE_CHECKING:
    import sublime  # type:ignore


class StGitlabProjectIssuesBoardCommand(sublime_plugin.TextCommand):
    def run(self, edit: sublime.Edit) -> None:
        panel = ProjectSelectPanel(callback=self.get_issues)
        panel.show_input()

    def get_issues(self, project_id: int) -> None:
        gitlab = utils.gl.get()
        project = gitlab.project(oid=project_id)
        per_page = utils.get_setting("list_page_size")
        query_params = {"project_id": project_id, "page": 1, "per_page": per_page, "state": "opened"}
        title = f"WIP:Issues Board: {project.name}"
        r = self.view.window().new_file()
        r.set_name(title)
        syntax_file = utils.get_setting("syntax_file")
        r.set_syntax_file(syntax_file)
        r.settings().set("query_params", query_params)
        r.settings().set("screen", utils.object_commands.get("issue", {}).get("screen_board"))
        r.settings().set("object_name", "issue")
        r.settings().set("word_wrap", False)
        r.settings().set("project_id", project_id)
        r.run_command("st_gitlab_project_issues_board_draw", {"title": title})
        r.set_scratch(True)
        r.set_read_only(True)
