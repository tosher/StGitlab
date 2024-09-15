#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

from __future__ import annotations
from typing import TYPE_CHECKING

import sublime  # type:ignore
from .stg_object import StGitlabObjectCommand

if TYPE_CHECKING:
    from ..libs.gitlab.v4.objects import ProjectMergeRequest  # type: ignore


class StGitlabMergeCommand(StGitlabObjectCommand):
    INPUT_STR = "Merge-request ID"
    object_name = "merge"

    def get_merge(self) -> ProjectMergeRequest:
        return self.gitlab.merge(project_id=self.project_id, oid=self.obj_id)


class StGitlabMergeDeleteCommand(StGitlabMergeCommand):
    VALID_SCREENS = {
        "merge": ["screen_view", "screen_list"],
    }

    INPUT_STR = "Merge Request ID to delete"

    def refresh(self) -> None:
        if self.screen == "st_gitlab_merges":
            self.view.run_command("st_gitlab_project_list_refresh")
        elif self.screen == "st_gitlab_merge":
            self.view.close()

    def process(self) -> None:
        if not self.obj_id:
            return
        is_del = sublime.ok_cancel_dialog(f"Are you really want to delete merge request #{self.obj_id}?")
        if not is_del:
            return
        mr = self.get_merge()
        mr.delete()
        self.refresh()
