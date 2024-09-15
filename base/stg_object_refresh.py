#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

from __future__ import annotations
from typing import TYPE_CHECKING

from . import utils
from .stg_object import StGitlabObjectTextCommand


if TYPE_CHECKING:
    import sublime  # type: ignore


class StGitlabObjectRefreshCommand(StGitlabObjectTextCommand):
    VALID_SCREENS = {
        "issue": ["screen_view"],
        "merge": ["screen_view"],
        "pipeline": ["screen_view"],
    }

    def run(self, edit: sublime.Edit) -> None:
        cursor = self.view.sel()[0]
        object_name = self.view.settings().get("object_name", None)
        object_id = self.view.settings().get("object_id", None)
        if object_id and object_name:
            self.view.erase_phantoms("shortcuts")
            self.view.erase_phantoms("label")
            cmd = utils.object_commands.get(object_name, {}).get("fetch")
            self.view.run_command(cmd, {"obj_id": object_id})
            self.view.sel().clear()
            self.view.sel().add(cursor)
            self.view.show(cursor)
