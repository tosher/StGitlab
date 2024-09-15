#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

from __future__ import annotations
from typing import TYPE_CHECKING

from . import utils
from .stg_user import UserSelectPanel
from .stg_object import StGitlabObjectTextCommand

if TYPE_CHECKING:
    from typing import List, Dict, Any
    import sublime  # type:ignore


class StGitlabProjectListFilterCommand(StGitlabObjectTextCommand):
    VALID_SCREENS = {
        "issue": ["screen_list"],
        "merge": ["screen_list"],
        "pipeline": ["screen_list"],
        "branch": ["screen_list"],
    }

    query_params: Dict[str, Any] = {}
    filter_name = None
    filter_values: List[str] = []
    project_id = None

    def run(self, edit: sublime.Edit) -> None:
        self.filter_types = utils.filter_types
        self.project_id = self.view.settings().get("project_id", None)
        self.view.window().show_quick_panel(list(self.filter_types.keys()), self.filter_done)

    def filter_done(self, filter_id: int) -> None:
        if filter_id < 0:
            return

        filter_type_key = list(self.filter_types.keys())[filter_id]
        self.filter_name = self.filter_types[filter_type_key]
        gitlab = utils.gl.get()

        self.filter_values = []
        filter_names: List[str] = []
        if self.filter_name in ["author_id", "assignee_id"]:
            panel = UserSelectPanel(callback=self.filter_user_done)
            panel.show_input()
            return
        elif self.filter_name == "labels":
            self.filter_values = [label.name for label in gitlab.labels(all=True)]
            filter_names = self.filter_values
        elif self.filter_name == "milestone":
            self.filter_values = [mile.title for mile in gitlab.milestones(all=True)]
            filter_names = self.filter_values
        elif self.filter_name == "state":
            self.filter_values = filter_names = ["opened", "closed"]
        elif filter_type_key == "Reset filters":
            query_params = self.view.settings().get("query_params", {})
            keys = list(query_params.keys())
            for key in keys:
                if key in list(self.filter_types.values()):
                    del query_params[key]
            self.get_list(query_params)
            self.view.window().status_message("All filters was cleared.")
            return

        if self.filter_values and filter_names:
            self.view.window().show_quick_panel(filter_names, self.filter_select_done)
        else:
            self.view.window().show_input_panel("Search:", "", self.filter_input_done, None, None)

    def filter_user_done(self, user_id: int) -> None:
        query_params = self.view.settings().get("query_params", {})
        query_params[self.filter_name] = user_id
        self.get_list(query_params)

    def filter_input_done(self, text: str) -> None:
        if not text:
            return
        query_params = self.view.settings().get("query_params", {})
        filter_value: Any = text
        if self.filter_name == "page":
            filter_value = int(text)

        query_params[self.filter_name] = filter_value
        self.get_list(query_params)

    def filter_select_done(self, idx: int) -> None:
        if idx < 0:
            return
        filter_value = self.filter_values[idx]
        query_params = self.view.settings().get("query_params", {})
        if self.filter_name == "labels":
            if self.filter_name in query_params:
                if filter_value not in query_params[self.filter_name]:
                    query_params[self.filter_name].append(filter_value)
            else:
                query_params[self.filter_name] = [filter_value]
        else:
            query_params[self.filter_name] = filter_value

        self.get_list(query_params)

    def get_list(self, query_params: Dict[str, Any]) -> None:
        per_page = utils.get_setting("list_page_size")
        query_params["per_page"] = per_page
        if self.filter_name != "state" and "state" not in query_params:
            query_params["state"] = "opened"
        if self.filter_name != "page" and "page" not in query_params:
            query_params["page"] = 1
        self.view.settings().set("query_params", query_params)
        self.view.run_command("st_gitlab_project_list_refresh")
