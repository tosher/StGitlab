#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

from __future__ import annotations
from typing import TYPE_CHECKING

from . import utils
from .stg_object import StGitlabObjectTextCommand

if TYPE_CHECKING:
    import sublime  # type:ignore


class StGitlabToggleSystemNotesCommand(StGitlabObjectTextCommand):
    VALID_SCREENS = {
        "issue": ["screen_view"],
        "merge": ["screen_view"],
    }

    def run(self, edit: sublime.Edit) -> None:
        is_show_system_notes = utils.get_setting("show_system_notes")
        if is_show_system_notes:
            utils.set_setting("show_system_notes", False)
        else:
            utils.set_setting("show_system_notes", True)
        self.view.run_command("st_gitlab_object_refresh")
