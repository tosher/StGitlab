#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

from __future__ import annotations
from typing import TYPE_CHECKING

from .stg_object import StGitlabObjectTextCommand

if TYPE_CHECKING:
    import sublime  # type:ignore


class StGitlabToggleSelectableCommand(StGitlabObjectTextCommand):
    VALID_SCREENS = {
        "issue": ["screen_view"],
        "merge": ["screen_view"],
        "pipeline": ["screen_view"],
    }

    def run(self, edit: sublime.Edit) -> None:
        is_unselectable = self.view.settings().get("st_gitlab_unselectable", True)
        if is_unselectable:
            self.view.settings().set("st_gitlab_unselectable", False)
        else:
            self.view.settings().set("st_gitlab_unselectable", True)
