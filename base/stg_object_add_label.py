#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

from __future__ import annotations
from typing import TYPE_CHECKING

from . import utils
from .stg_object import StGitlabObjectTextCommand

if TYPE_CHECKING:
    import sublime  # type:ignore


class StGitlabObjectAddLabelCommand(StGitlabObjectTextCommand):
    VALID_SCREENS = {
        "issue": ["screen_view"],
        "merge": ["screen_view"],
    }

    def run(self, edit: sublime.Edit) -> None:
        def on_done(i: int) -> None:
            if i < 0:
                return

            if obj is None:
                return

            self.gitlab.label_add(labels_names[i], obj)
            self.view.run_command("st_gitlab_object_refresh")

        self.gitlab = utils.gl.get()
        obj = self.gitlab.object_by_view()
        if obj is None:
            raise ValueError("Add label failed: view object not found")

        obj_labels = obj.attributes.get("labels", [])
        labels = self.gitlab.labels(all=True)
        labels_names = [lab.name for lab in labels if lab.name not in obj_labels]
        self.view.window().show_quick_panel(labels_names, on_done)
