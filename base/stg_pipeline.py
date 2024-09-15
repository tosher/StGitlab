#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

from __future__ import annotations
from typing import TYPE_CHECKING

import sublime  # type:ignore

from . import utils
from .stg_object import StGitlabObjectCommand

if TYPE_CHECKING:
    from typing import Any
    from ..libs.gitlab.v4.objects import ProjectPipeline  # type: ignore


class StGitlabPipelineCommand(StGitlabObjectCommand):
    VALID_SCREENS = {
        "pipeline": ["screen_view", "screen_list"],
    }

    INPUT_STR = "Pipeline ID"
    object_name = "pipeline"

    def get_pipeline(self) -> ProjectPipeline:
        return self.gitlab.pipeline(project_id=self.project_id, oid=self.obj_id)

    def refresh(self) -> None:
        if self.screen == utils.object_commands.get("pipeline", {}).get("screen_list"):
            self.view.run_command("st_gitlab_project_list_refresh")
        elif self.screen == utils.object_commands.get("pipeline", {}).get("screen_view"):
            self.view.run_command("st_gitlab_object_refresh")


class StGitlabPipelineCancelCommand(StGitlabPipelineCommand):
    INPUT_STR = "Pipeline ID to cancel"

    def process(self) -> None:
        if not self.obj_id:
            return
        is_cancel = sublime.ok_cancel_dialog(f"Are you really want to cancel pipeline #{self.obj_id}?")
        if not is_cancel:
            return
        pl = self.get_pipeline()
        pl.cancel()
        self.refresh()


class StGitlabPipelineRetryCommand(StGitlabPipelineCommand):
    INPUT_STR = "Pipeline ID to retry"

    def process(self) -> None:
        if not self.obj_id:
            return
        is_cancel = sublime.ok_cancel_dialog(f"Are you want to retry pipeline #{self.obj_id}?")
        if not is_cancel:
            return
        pl = self.get_pipeline()
        pl.retry()
        self.refresh()


class StGitlabPipelineDeleteCommand(StGitlabPipelineCommand):
    INPUT_STR = "Pipeline ID to delete"

    def refresh(self) -> None:
        if self.screen == "st_gitlab_pipelines":
            self.view.run_command("st_gitlab_project_list_refresh")
        elif self.screen == "st_gitlab_pipeline":
            self.view.close()

    def process(self) -> None:
        if not self.obj_id:
            return
        is_del = sublime.ok_cancel_dialog(f"Are you really want to delete pipeline #{self.obj_id}?")
        if not is_del:
            return
        pipeline = self.get_pipeline()
        pipeline.delete()
        self.refresh()

    def is_visible(self, *args: Any) -> bool:
        screen = self.view.settings().get("screen")
        if not screen:
            return False
        valid_screens = [
            utils.object_commands.get("pipeline", {}).get("screen_view"),
            utils.object_commands.get("pipeline", {}).get("screen_list"),
        ]
        if screen in valid_screens:
            return True
        return False
