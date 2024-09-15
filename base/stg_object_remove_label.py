#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

from __future__ import annotations
from typing import TYPE_CHECKING

from . import utils
from .stg_object import StGitlabObjectTextCommand

if TYPE_CHECKING:
    import sublime  # type:ignore


class StGitlabObjectRemoveLabelCommand(StGitlabObjectTextCommand):
    VALID_SCREENS = {
        "issue": ["screen_view"],
        "merge": ["screen_view"],
    }

    def run(self, edit: sublime.Edit) -> None:
        def on_done(idx: int) -> None:
            if idx < 0:
                return

            self.gitlab.label_del(obj_labels[idx], obj)
            self.view.run_command("st_gitlab_object_refresh")

        self.gitlab = utils.gl.get()
        obj = self.gitlab.object_by_view()
        obj_labels = obj.attributes.get("labels", [])
        self.view.window().show_quick_panel(obj_labels, on_done)
