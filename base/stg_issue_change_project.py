#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

from __future__ import annotations
from typing import TYPE_CHECKING

from . import utils
from .stg_object import StGitlabObjectTextCommand
from .stg_project import ProjectSelectPanel

if TYPE_CHECKING:
    import sublime  # type:ignore


class StGitlabChangeProjectCommand(StGitlabObjectTextCommand):
    VALID_SCREENS = {
        "issue": ["screen_view"],
    }

    def run(self, edit: sublime.Edit) -> None:
        def on_done(project_id_new: int) -> None:
            """
            project_id_new - only project ID, not `namespce/project_name`
            """
            if not project_id_new:
                return

            project_new = gitlab.project(oid=project_id_new)
            issue.move(project_id_new)

            self.view.settings().set("project_id", project_new.id)
            self.view.settings().set("object_id", issue.iid)
            self.view.window().status_message(f"Issue #{issue.id} was moved to {project_new.name}")
            self.view.run_command("st_gitlab_object_refresh")

        gitlab = utils.gl.get()
        project = gitlab.project()
        issue = gitlab.issue()
        if project and issue:
            panel = ProjectSelectPanel(callback=on_done)
            panel.show_input()
