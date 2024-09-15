#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

from __future__ import annotations
from typing import TYPE_CHECKING
import sublime  # type:ignore

from . import utils

if TYPE_CHECKING:
    from typing import Callable, Optional, List
    from ..libs.gitlab.v4.objects import Project  # type: ignore


class ProjectSelectPanel(object):
    def __init__(self, callback: Optional[Callable] = None, required: bool = True) -> None:
        self.callback = callback
        self.required = required
        self.window = sublime.active_window()

    def show_input(self) -> None:
        projects_menu = ["All projects", "Custom"]

        self.projects_filter = utils.get_setting("projects_filter", [])

        if self.projects_filter:
            projects_menu[0] = "All projects (filtered)"

        if not self.required:
            projects_menu.append("No project")

        self.window.show_quick_panel(projects_menu, self.get_project)

    def get_project(self, idx: int) -> None:
        if idx < 0:
            return
        gitlab = utils.gl.get()

        if idx == 0:
            if self.projects_filter:
                projects = [gitlab.project(oid=pid) for pid in self.projects_filter]
            else:
                projects = gitlab.projects(all=True)
            self.set_projects([pr for pr in projects if pr is not None])

        elif idx == 1:
            self.window.show_input_panel("Project:", "", self.get_custom_project_done, None, None)
        elif idx == 2 and self.callback is not None:
            sublime.set_timeout_async(self.callback(None), 0)

    def get_custom_project_done(self, project_id: int) -> None:
        gitlab = utils.gl.get()
        project = gitlab.project(oid=project_id)
        if project:
            self.set_projects([project])
            return

        self.set_projects([])

    def set_projects(self, projects: List[Project]) -> None:
        self.prj_names = []
        self.prj_ids = []
        for prj in projects:
            self.prj_names.append(prj.name)
            self.prj_ids.append(prj.id)

        if len(projects) == 1:
            self.on_done(0)
        else:
            self.window.show_quick_panel(self.prj_names, self.on_done)

    def on_done(self, idx: int) -> None:
        if idx < 0:
            return
        project_id = self.prj_ids[idx]

        if self.callback is None:
            return

        sublime.set_timeout_async(self.callback(project_id), 0)
