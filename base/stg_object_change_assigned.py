#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

from __future__ import annotations
from typing import TYPE_CHECKING

from . import utils
from .stg_user import UserSelectPanel
from .stg_object import StGitlabObjectTextCommand

if TYPE_CHECKING:
    import sublime  # type: ignore


class StGitlabObjectChangeAssignedCommand(StGitlabObjectTextCommand):
    VALID_SCREENS = {
        "issue": ["screen_view"],
        "merge": ["screen_view"],
    }

    def run(self, edit: sublime.Edit) -> None:
        panel = UserSelectPanel(callback=self.assign)
        panel.show_input()

    def assign(self, user_id: int) -> None:
        gitlab = utils.gl.get()
        obj = gitlab.object_by_view()
        gitlab.assignee_set(user_id, obj)
        self.view.run_command("st_gitlab_object_refresh")
