#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

import sublime  # type:ignore

from . import utils
from .stg_object import StGitlabObjectTextCommand


class StGitlabProjectListRefreshCommand(StGitlabObjectTextCommand):
    VALID_SCREENS = {
        "issue": ["screen_list"],
        "merge": ["screen_list"],
        "pipeline": ["screen_list"],
        "branch": ["screen_list"],
    }

    def run(self, edit: sublime.Edit) -> None:
        cursor = self.view.sel()[0]
        query_params = self.view.settings().get("query_params")
        per_page = utils.get_setting("list_page_size")
        query_params["per_page"] = per_page
        if query_params:
            self.view.settings().set("query_params", query_params)
            title = self.view.name()
            self.view.set_read_only(False)
            self.view.erase(edit, sublime.Region(0, self.view.size()))
            object_name = self.view.settings().get("object_name")
            cmd = utils.object_commands.get(object_name, {}).get("list")
            self.view.run_command(cmd, {"title": title})
            self.view.sel().clear()
            self.view.sel().add(cursor)
            self.view.show(cursor)
            self.view.set_read_only(True)
            self.view.window().status_message(f"{object_name.title()}s list was refreshed")
