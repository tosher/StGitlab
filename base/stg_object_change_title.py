#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

from __future__ import annotations
from typing import TYPE_CHECKING

from . import utils
from .stg_object import StGitlabObjectTextCommand

if TYPE_CHECKING:
    import sublime  # type: ignore


class StGitlabObjectChangeTitleCommand(StGitlabObjectTextCommand):
    VALID_SCREENS = {
        "issue": ["screen_view"],
        "merge": ["screen_view"],
    }

    def run(self, edit: sublime.Edit) -> None:
        def on_done(text: str) -> None:
            if text is not None:
                obj.title = text
                obj.save()
                self.view.run_command("st_gitlab_object_refresh")

        gitlab = utils.gl.get()
        obj = gitlab.object_by_view()
        self.view.window().show_input_panel("Title:", obj.title, on_done, None, None)
