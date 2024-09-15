#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

from __future__ import annotations
from typing import TYPE_CHECKING
import re

from . import utils
from .stg_object import StGitlabObjectTextCommand

if TYPE_CHECKING:
    import sublime  # type: ignore


class StGitlabMergeToggleWipCommand(StGitlabObjectTextCommand):
    VALID_SCREENS = {
        "merge": ["screen_view"],
    }

    def run(self, edit: sublime.Edit) -> None:
        gitlab = utils.gl.get()
        project = gitlab.project()
        merge = gitlab.merge()
        if project and merge:
            val = False if merge.attributes.get("work_in_progress") else True
            title = merge.attributes.get("title")
            title = f"WIP:{title}" if val else re.sub(r"^wip[:\s]", "", title, flags=re.IGNORECASE)
            merge.save(title=title)
        self.view.run_command("st_gitlab_object_refresh")
