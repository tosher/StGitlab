#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

from __future__ import annotations
from typing import TYPE_CHECKING
import copy
import sublime  # type:ignore
import sublime_plugin  # type:ignore

from . import utils
from . import types

if TYPE_CHECKING:
    from typing import Any, Optional, Dict


class EditboxSaveCommand(sublime_plugin.TextCommand):
    def run(self, edit: sublime.Edit) -> None:
        text = self.view.substr(sublime.Region(0, self.view.size()))
        cmd = self.view.settings().get("on_done")
        layout = self.view.settings().get("base_layout")
        base_id = self.view.settings().get("base_id")
        obj_kwargs = self.view.settings().get("obj_kwargs", None)
        eb = Editbox(base_id)
        if eb.view is None:
            raise ValueError("Editbox view is undefined")
        eb.view.run_command(cmd, {"text": text, "obj_kwargs": obj_kwargs})
        eb.layout_base(layout)

    def is_visible(self, *args: Any) -> bool:
        screen = self.view.settings().get("screen")
        if not screen:
            return False
        if screen in ["editbox"]:
            return True
        return False


class EditboxCancelCommand(sublime_plugin.TextCommand):
    def run(self, edit: sublime.Edit) -> None:
        is_del = sublime.ok_cancel_dialog("Are you really want to cancel editing?")
        if not is_del:
            return
        base_id = self.view.settings().get("base_id")
        layout = self.view.settings().get("base_layout")
        eb = Editbox(base_id)
        eb.layout_base(layout)

    def is_visible(self, *args: Any) -> bool:
        screen = self.view.settings().get("screen")
        if not screen:
            return False
        if screen in ["editbox"]:
            return True
        return False


class Editbox(object):
    def __init__(self, base_id: int, syntax_auto: bool = False, height: Optional[int] = None) -> None:
        self.base_id = base_id
        self.view = self.view_base()
        if self.view is None:
            raise ValueError("Editbox view is undefined")
        self.window: sublime.Window = self.view.window()
        self.syntax_auto = syntax_auto
        self.height = height

    def edit(self, title: str, on_done: str, text: Optional[str] = None, **kwargs: Any) -> None:
        """
        on_done - command name to call on done
        """

        if not text:
            text = ""
        self.base_layout = self.layout()
        self.base_group = self.window.active_group()
        self.layout_edit()
        self.editbox = self.window.new_file()
        self.editbox.set_name(title)
        self.editbox.set_scratch(True)
        if not self.syntax_auto:
            syntax_file = utils.get_setting("syntax_file_edit")
            if syntax_file:
                self.editbox.set_syntax_file(syntax_file)
        else:
            syntax_file = self.auto_syntax(title)
            if syntax_file:
                self.editbox.set_syntax_file(syntax_file)
        self.editbox.settings().set("on_done", on_done)
        self.editbox.settings().set("base_id", self.base_id)
        self.editbox.settings().set("screen", "editbox")
        self.editbox.settings().set("word_wrap", True)
        self.editbox.settings().set("base_layout", self.base_layout)
        self.editbox.settings().set("obj_kwargs", kwargs)
        self.editbox.run_command(utils.get_setting("insert_text_command"), {"position": 0, "text": text})

    def auto_syntax(self, name: str) -> Optional[str]:
        return utils.syntaxes.get(name.split(".")[-1])

    def layout(self) -> Dict[str, types.Value]:
        return self.window.layout()

    def is_active(self) -> bool:
        if hasattr(self, "editbox"):
            return True
        views = sublime.active_window().views()
        for view in views:
            if view.settings().get("screen", "") == "editbox":
                return True
        return False

    def focus_base(self) -> None:
        self.window.focus_view(self.view)

    def view_base(self) -> sublime.View:
        views = sublime.active_window().views()
        for view in views:
            if view.id() == self.base_id:
                return view

    def view_editbox(self) -> sublime.View:
        if hasattr(self, "editbox"):
            self.editbox
        views = sublime.active_window().views()
        for view in views:
            if view.settings().get("screen", "") == "editbox":
                return view

    def get_editbox_height(self) -> float:
        h = self.height if self.height else utils.get_setting("edit_height_percent")

        ratio = (100 - int(h)) / 100
        return ratio

    def add_row_cell(self, layout: Dict[str, types.Value]) -> Dict[str, types.Value]:
        if not isinstance(layout["rows"], list):
            return layout

        if not isinstance(layout["cols"], list):
            return layout

        if not isinstance(layout["cells"], list):
            return layout

        height_prev_row = layout["rows"][-2]

        if not isinstance(height_prev_row, (int, float)):
            return layout

        height_eb = height_prev_row + self.get_editbox_height()
        layout["rows"].insert(-1, height_eb)

        rows = len(layout["rows"]) - 1
        cols = len(layout["cols"]) - 1
        layout["cells"].append([0, rows - 1, cols, rows])
        return layout

    def layout_edit(self) -> None:
        layout = copy.deepcopy(self.base_layout)
        self.add_row_cell(layout)
        self.window.run_command("set_layout", layout)
        # set focus to last group
        self.window.focus_group(-1)

    def layout_base(self, layout: Dict[str, types.Value]) -> None:
        self.base_layout = layout
        self.view_editbox().close()
        self.focus_base()
        self.window.run_command("set_layout", self.base_layout)
