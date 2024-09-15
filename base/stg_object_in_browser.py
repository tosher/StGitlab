#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

from __future__ import annotations
from typing import TYPE_CHECKING
import webbrowser

from . import utils
from .stg_object import StGitlabObjectTextCommand

if TYPE_CHECKING:
    import sublime  # type: ignore


# Gitlab Object: Open in Browser
class StGitlabObjectInBrowserCommand(StGitlabObjectTextCommand):
    VALID_SCREENS = {
        "issue": ["screen_view"],
        "merge": ["screen_view"],
        "pipeline": ["screen_view"],
    }

    def run(self, edit: sublime.Edit) -> None:
        gitlab = utils.gl.get()
        project = gitlab.project()
        if project is None:
            raise ValueError("Project is not defined")

        screen = self.view.settings().get("screen")
        web_url = None
        if screen == "st_gitlab_issue":
            obj = gitlab.issue()
            web_url = obj.attributes.get("web_url")
        elif screen == "st_gitlab_merge":
            obj = gitlab.merge()
            web_url = obj.attributes.get("web_url")
        elif screen == "st_gitlab_pipeline":
            # url not exists in api now
            obj = gitlab.pipeline()
            gl_url = utils.get_setting("gitlab_url")
            project_path = project.attributes.get("path_with_namespace")
            web_url = f"{gl_url}/{project_path}/pipelines/{obj.id}"
        if web_url is not None:
            webbrowser.open(web_url)
