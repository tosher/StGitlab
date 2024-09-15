#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

from __future__ import annotations
from typing import TYPE_CHECKING
from io import BytesIO

import sublime_plugin  # type:ignore

from . import utils
from .editbox import Editbox
from .stg_object import StGitlabObjectTextCommand

if TYPE_CHECKING:
    from typing import Dict, Any
    import sublime  # type:ignore


class StGitlabSnippetChangeFileCommand(StGitlabObjectTextCommand):
    VALID_SCREENS = {
        "snippet": ["screen_view"],
    }

    def run(self, edit: sublime.Edit) -> None:
        gitlab = utils.gl.get()
        project = gitlab.project()
        obj = gitlab.object_by_view()
        raw = obj.content()
        fp = BytesIO(raw)
        text = fp.read().decode("utf-8").replace("\r", "")
        on_done = "st_gitlab_snippet_change_file_done"
        eb = Editbox(self.view.id(), syntax_auto=True, height=80)
        eb.edit(
            obj.file_name,
            on_done,
            text,
            project_id=project.id if project else None,
            object_id=obj.iid if hasattr(obj, "iid") else obj.id,
        )


class StGitlabSnippetChangeFileDoneCommand(sublime_plugin.TextCommand):
    def run(self, edit: sublime.Edit, text: str, obj_kwargs: Dict[str, Any]) -> None:
        gitlab = utils.gl.get(self.view)
        obj = gitlab.object_by_view()
        obj.content = text
        obj.save()
        self.view.run_command("st_gitlab_object_refresh")
