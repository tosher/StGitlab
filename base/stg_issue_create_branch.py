#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

from __future__ import annotations
from typing import TYPE_CHECKING

from . import utils
from .stg_object import StGitlabObjectTextCommand

from transliterate import translit  # type: ignore

if TYPE_CHECKING:
    import sublime  # type: ignore


class StGitlabIssueCreateBranchCommand(StGitlabObjectTextCommand):
    VALID_SCREENS = {
        "issue": ["screen_view"],
    }

    def run(self, edit: sublime.Edit) -> None:
        def on_done(name: str) -> None:
            if not name:
                return

            project.branches.create({"branch": name, "ref": "master"})
            self.view.run_command("st_gitlab_object_refresh")

        gitlab = utils.gl.get()
        project = gitlab.project()
        self.issue = gitlab.issue()
        branch_name = f"{self.issue.iid}-{self.get_branch_name()}"
        if self.issue:
            self.view.window().show_input_panel("Title:", branch_name, on_done, None, None)

    def get_branch_name(self) -> str:
        translit_lang = utils.get_setting("issue_to_branch_transliterate_lang")
        if not translit_lang:
            return ""
        return translit(self.issue.title, translit_lang, reversed=True).replace("'", "").replace(".", "").replace(" ", "-")
