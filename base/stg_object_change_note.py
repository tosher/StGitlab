#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

from __future__ import annotations
from typing import TYPE_CHECKING

import sublime  # type: ignore
import sublime_plugin  # type: ignore

from . import utils
from .editbox import Editbox
from .stg_object import StGitlabObjectTextCommand

if TYPE_CHECKING:
    from typing import Any, Dict


class StGitlabObjectChangeNoteCommand(StGitlabObjectTextCommand):
    VALID_SCREENS = {
        "issue": ["screen_view"],
        "merge": ["screen_view"],
    }

    def run(self, edit: sublime.Edit, note_id: int) -> None:
        if not note_id:
            return
        gitlab = utils.gl.get()
        project = gitlab.project()
        obj = gitlab.object_by_view()
        note = obj.notes.get(note_id)
        if note.attributes.get("system", False):
            sublime.message_dialog("Unable to edit system message.")
            return
        on_done = "st_gitlab_object_change_note_done"
        eb = Editbox(self.view.id())
        eb.edit(
            f"Note {note_id}",
            on_done,
            note.attributes.get("body", ""),
            project_id=project.id if project else None,
            object_id=obj.iid if hasattr(obj, "iid") else obj.id,
            note_id=note_id,
        )


class StGitlabObjectChangeNoteDoneCommand(sublime_plugin.TextCommand):
    def run(self, edit: sublime.Edit, text: str, obj_kwargs: Dict[str, Any]) -> None:
        note_id = obj_kwargs.get("note_id")
        gitlab = utils.gl.get(self.view)
        obj = gitlab.object_by_view()
        note = obj.notes.get(note_id)
        if not hasattr(note, "save"):
            sublime.message_dialog(f"Note save for {obj.__class__.__name__} is not supported")
            return
        note.body = text
        note.save()
        self.view.run_command("st_gitlab_object_refresh")
