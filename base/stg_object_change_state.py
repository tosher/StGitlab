#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

from __future__ import annotations
from typing import TYPE_CHECKING

from . import utils
from .stg_object import StGitlabObjectTextCommand

if TYPE_CHECKING:
    import sublime  # type: ignore


class StGitlabObjectChangeStateCommand(StGitlabObjectTextCommand):
    VALID_SCREENS = {
        "issue": ["screen_view"],
        "merge": ["screen_view"],
    }

    states = ["opened", "closed"]
    state_events = ["reopen", "close"]

    def run(self, edit: sublime.Edit) -> None:
        def on_done(state_idx: int) -> None:
            if state_idx < 0:
                return

            obj.state_event = self.state_events[state_idx]
            obj.save()
            self.view.run_command("st_gitlab_object_refresh")

        gitlab = utils.gl.get()
        obj = gitlab.object_by_view()
        self.view.window().show_quick_panel(self.states, on_done)
