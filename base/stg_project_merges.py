#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

from __future__ import annotations
from typing import TYPE_CHECKING

import sublime_plugin  # type:ignore

from . import utils
from .stg_project import ProjectSelectPanel

if TYPE_CHECKING:
    import sublime  # type:ignore


class StGitlabProjectMergesCommand(sublime_plugin.TextCommand):
    def run(self, edit: sublime.Edit) -> None:
        panel = ProjectSelectPanel(callback=self.get_merges)
        panel.show_input()

    def get_merges(self, project_id: int) -> None:
        gitlab = utils.gl.get()
        project = gitlab.project(oid=project_id)
        per_page = utils.get_setting("list_page_size")
        query_params = {"project_id": project_id, "page": 1, "per_page": per_page, "state": "opened"}
        title = f"Merge-requests: {project.name}"
        r = self.view.window().new_file()
        r.set_name(title)
        syntax_file = utils.get_setting("syntax_file")
        r.set_syntax_file(syntax_file)
        r.settings().set("query_params", query_params)
        r.settings().set("screen", utils.object_commands.get("merge", {}).get("screen_list"))
        r.settings().set("object_name", "merge")
        r.settings().set("word_wrap", False)
        r.settings().set("project_id", project_id)
        cmd = utils.object_commands.get("merge", {}).get("list")
        r.run_command(cmd, {"title": title})
        r.set_scratch(True)
        # r.run_command('st_gitlab_view_show_labels')
        r.set_read_only(True)
