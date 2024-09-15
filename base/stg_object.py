#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

from __future__ import annotations
from typing import TYPE_CHECKING
import sublime_plugin  # type:ignore

from . import utils
from .stg_project import ProjectSelectPanel

if TYPE_CHECKING:
    from typing import Optional, Any, List, Dict
    import sublime  # type:ignore


class StGitlabObjectTextCommand(sublime_plugin.TextCommand):
    VALID_SCREENS: Dict[str, List[str]] = {}

    @property
    def valid_screens(self) -> List[str]:
        """
        Allowed plugin screens to call a command
        """
        valid_screens: List[str] = []
        for obj, screens in self.VALID_SCREENS.items():
            for screen_name in screens:
                screen = utils.object_commands.get(obj, {}).get(screen_name)
                if screen is None:
                    continue
                valid_screens.append(screen)

        return valid_screens

    def is_visible(self, *args: Any) -> bool:
        """
        Command visibility in Command Palette
        """
        screen = self.view.settings().get("screen")
        if not screen:
            return False
        if screen in self.valid_screens:
            return True
        return False


class StGitlabObjectCommand(StGitlabObjectTextCommand):
    INPUT_STR = "Object ID"
    object_name = ""
    project_required = True

    def run(self, edit: sublime.Edit, obj_id: Optional[int] = None) -> None:
        self.obj_id = obj_id
        self.gitlab = utils.gl.get()
        cmds = utils.object_commands.get(self.object_name, {})
        self.screen_list = cmds.get("screen_list")
        self.screen_view = cmds.get("screen_view")
        self.cmd_fetcher = cmds.get("fetch")
        self.get_project_id()

    def get_obj_id(self) -> None:
        if self.obj_id:
            return
        self.screen = self.view.settings().get("screen", None)
        if self.screen == self.screen_list:
            colsep = utils.get_setting("table_column_separator")
            try:
                line = self.view.substr(self.view.line(self.view.sel()[0].end()))
                obj_id = line.split(colsep)[1].strip()
                if not obj_id.isdigit():
                    raise ValueError(f"Get object id failed, invalid value: {self.obj_id}")
                self.obj_id = int(obj_id)
            except Exception:
                pass
        elif self.screen == self.screen_view:
            self.obj_id = self.view.settings().get("object_id", None)

        if not self.obj_id:
            self.view.window().show_input_panel(self.INPUT_STR, "", self.obj_done, None, None)
        else:
            self.obj_done(self.obj_id)

    def obj_done(self, obj_id: int) -> None:
        self.obj_id = obj_id
        self.process()

    def get_project_id(self) -> None:
        project_id = self.view.settings().get("project_id", None)
        if project_id:
            self.project_done(project_id)
        else:
            panel = ProjectSelectPanel(callback=self.project_done, required=self.project_required)
            panel.show_input()

    def project_done(self, project_id: int) -> None:
        self.project_id = project_id
        self.get_obj_id()

    def process(self) -> None:
        if not self.obj_id:
            return
        self.view.run_command(self.cmd_fetcher, {"project_id": self.project_id, "obj_id": self.obj_id})
