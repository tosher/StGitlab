#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

from __future__ import annotations
from typing import TYPE_CHECKING

import sublime_plugin  # type: ignore

from . import utils
from .editbox import Editbox
from .stg_object import StGitlabObjectTextCommand

if TYPE_CHECKING:
    from typing import Any
    import sublime  # type: ignore


class StGitlabObjectChangeDescriptionCommand(StGitlabObjectTextCommand):
    VALID_SCREENS = {
        "issue": ["screen_view"],
        "merge": ["screen_view"],
    }

    def run(self, edit: sublime.Edit) -> None:
        gitlab = utils.gl.get()
        project = gitlab.project()
        obj = gitlab.object_by_view()
        on_done = "st_gitlab_object_change_description_done"
        eb = Editbox(self.view.id())
        eb.edit(
            "Description",
            on_done,
            obj.description or None,
            project_id=project.id if project else None,
            object_id=obj.iid if hasattr(obj, "iid") else obj.id,
        )


class StGitlabObjectChangeDescriptionDoneCommand(sublime_plugin.TextCommand):
    def run(self, edit: sublime.Edit, text: str, obj_kwargs: Any) -> None:
        gitlab = utils.gl.get(self.view)
        obj = gitlab.object_by_view()
        obj.description = text
        obj.save(title=obj.title)
        self.view.run_command("st_gitlab_object_refresh")
