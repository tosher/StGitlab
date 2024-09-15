#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

from __future__ import annotations
from typing import TYPE_CHECKING

import sublime_plugin  # type:ignore

# NOTE: tabulate exists in repos, but old v0.7.5 version (no support for `outline` table)
# https://packagecontrol.github.io/channel/channel_v4.json
from tabulate import tabulate  # type:ignore

from . import utils
from .st_shortcuts_menu import StShortcutsMenu  # type:ignore

if TYPE_CHECKING:
    from typing import List, Dict, Any
    import sublime  # type: ignore
    from ..libs.gitlab.v4.objects import (  # type: ignore
        Issue,
        ProjectMergeRequest,
        ProjectPipeline,
        ProjectBranch,
        Snippet,
        User,
    )


left_arrow = utils.get_setting("char_left_arrow")
right_arrow = utils.get_setting("char_right_arrow")


class StGitlabProjectObjectsListCommand(sublime_plugin.TextCommand):
    def run(self, edit: sublime.Edit, title: str) -> None:
        self.title = title
        self.gitlab = utils.gl.get()
        self.query_params = self.view.settings().get("query_params", {})
        self.objects = self.get_objects()
        self.build()

    def build(self) -> None:
        self.show_shortcuts()
        content = "\n"
        content += self.show_header()
        content += self.show_filters()
        content += '\n> Set "Luicida Console" font if table is misaligned!\n'
        content += self.show_table()
        self.view.run_command("st_gitlab_insert_text", {"position": 0, "text": content})
        self.view.show(0)

    def show_shortcuts(self) -> None:
        StShortcutsMenu(self.view, shortcuts=self.shortcuts(), cols=self.cols())

    def show_header(self) -> str:
        header = "\n"
        header += f"## {self.title}\n"
        header += f"\t**Total**: {len(self.objects)}\n"
        page = self.query_params.get("page")
        per_page = self.query_params.get("per_page")
        header += f"\t**Page number**: {page} ({per_page} per page)\n"
        return header

    def show_filters(self) -> str:
        filters = "\t**Filters**:\n"
        for name in utils.filter_types.values():
            if name in self.query_params:
                if name == "labels":
                    lbl_char = utils.get_setting("label_char")
                    labels = ", ".join([f"{lbl_char}{label}{lbl_char}" for label in self.query_params.get(name)])
                    filters += f"\t\t**{name}**: {labels}\n"
                else:
                    filters += f"\t\t**{name}**: {self.query_params.get(name)}\n"
        return filters

    def get_columns_properties(self) -> List[Dict[str, str]]:
        return []

    def show_table(self) -> str:
        cols = self.get_columns_properties()
        tbl_header = [col["colname"] for col in cols]
        cols_special = self.special_cols()
        table_data = []

        for obj in self.objects:
            row = []
            for col in cols:
                if col.get("special", False):
                    row.append(cols_special.get(getattr(obj, col["key"]), {}).get(col["prop"], ""))
                else:
                    row.append(utils.stg_get_property_value(obj, col))
            table_data.append(row)

        table = tabulate(
            table_data,
            tablefmt="rounded_outline",
            headers=tbl_header,
            # colalign=["default", "default", "right", "right", "right", "right"],
        )
        return table

    def get_objects(self) -> List[Any]:
        return []

    def special_cols(self) -> Dict[str, Any]:
        return {}


class StGitlabProjectIssuesListCommand(StGitlabProjectObjectsListCommand):
    @classmethod
    def shortcuts(cls) -> Dict[str, List[str]]:
        return {
            "new": ["n", "new"],
            "open": ["Enter", "open"],
            "refresh": ["F5", "refresh"],
            "delete": ["Delete", "delete"],
            "filter": ["f", "filter"],
            "labeladd": ["l", "add label"],
            "labeldel": ["Alt+l", "delete label"],
            "mileset": ["m", "set milestone"],
            "miledel": ["Alt+m", "unset milestone"],
            "assigneeset": ["a", "set assignee"],
            "assigneedel": ["Alt+a", "unset assignee"],
            "ppage": [f"Shift+{left_arrow}", "prev. page"],
            "npage": [f"Shift+{right_arrow}", "next page"],
        }

    @classmethod
    def cols(cls) -> List[List[str]]:
        cols = [
            ["refresh", "new", "filter"],
            ["labeladd", "mileset", "assigneeset"],
            ["labeldel", "miledel", "assigneedel"],
            ["open", "delete"],
            ["ppage", "npage"],
        ]
        return cols

    def get_objects(self) -> List[Issue]:
        return self.gitlab.issues(**self.query_params)

    def get_columns_properties(self) -> List[Dict[str, str]]:
        return utils.get_setting("issue_list_columns", {})


class StGitlabProjectMergesListCommand(StGitlabProjectObjectsListCommand):
    @classmethod
    def shortcuts(cls) -> Dict[str, List[str]]:
        return {
            "new": ["n", "new"],
            "open": ["Enter", "open"],
            "refresh": ["F5", "refresh"],
            "delete": ["Delete", "delete"],
            "filter": ["f", "filter"],
            "labeladd": ["l", "add label"],
            "labeldel": ["Alt+l", "delete label"],
            "mileset": ["m", "set milestone"],
            "miledel": ["Alt+m", "unset milestone"],
            "assigneeset": ["a", "set assignee"],
            "assigneedel": ["Alt+a", "unset assignee"],
            "ppage": [f"Shift+{left_arrow}", "prev. page"],
            "npage": [f"Shift+{right_arrow}", "next page"],
        }

    @classmethod
    def cols(cls) -> List[List[str]]:
        cols = [
            ["open", "refresh", "new", "delete"],
            ["labeladd", "mileset", "assigneeset"],
            ["labeldel", "miledel", "assigneedel"],
            ["filter", "ppage", "npage"],
        ]
        return cols

    def get_objects(self) -> List[ProjectMergeRequest]:
        return self.gitlab.merges(**self.query_params)

    def get_columns_properties(self) -> List[Dict[str, str]]:
        return utils.get_setting("merge_requests_list_columns", {})


class StGitlabProjectPipelinesListCommand(StGitlabProjectObjectsListCommand):
    @classmethod
    def shortcuts(cls) -> Dict[str, List[str]]:
        return {
            "open": ["Enter", "open"],
            "refresh": ["F5", "refresh"],
            "retry": ["b", "retry"],
            "cancel": ["c", "cancel"],
            "delete": ["Delete", "delete"],
            "filter": ["f", "filter"],
            "ppage": [f"Shift+{left_arrow}", "prev. page"],
            "npage": [f"Shift+{right_arrow}", "next page"],
        }

    @classmethod
    def cols(cls) -> List[List[str]]:
        cols = [["open"], ["refresh", "filter"], ["retry", "cancel", "delete"], ["ppage", "npage"]]
        return cols

    def get_objects(self) -> List[ProjectPipeline]:
        return self.gitlab.pipelines(**self.query_params)

    def get_columns_properties(self) -> List[Dict[str, str]]:
        return utils.get_setting("pipelines_list_columns", {})


class StGitlabProjectBranchesListCommand(StGitlabProjectObjectsListCommand):
    @classmethod
    def shortcuts(cls) -> Dict[str, List[str]]:
        return {
            "refresh": ["F5", "refresh"],
            "merge": ["m", "merge-request"],
            "toggleprotect": ["p", "toggle protect"],
            "filter": ["f", "filter"],
            "ppage": [f"Shift+{left_arrow}", "prev. page"],
            "npage": [f"Shift+{right_arrow}", "next page"],
        }

    @classmethod
    def cols(cls) -> List[List[str]]:
        cols = [["refresh", "filter"], ["merge", "toggleprotect"], ["ppage", "npage"]]
        return cols

    def get_objects(self) -> List[ProjectBranch]:
        return self.gitlab.branches(**self.query_params)

    def get_columns_properties(self) -> List[Dict[str, str]]:
        return utils.get_setting("branches_list_columns", {})

    def special_cols(self) -> Dict[str, Any]:
        cols = {}
        project = self.gitlab.project()
        for branch in self.objects:
            cols[branch.name] = {}
            if branch.name == "master":
                cols[branch.name]["behind"] = 0
                cols[branch.name]["ahead"] = 0
                cols[branch.name]["commits_summary"] = ""
            else:
                compare_result_ahead = project.repository_compare("master", branch.name)
                compare_result_behind = project.repository_compare(branch.name, "master")
                cols[branch.name]["ahead"] = len(compare_result_ahead["commits"])
                cols[branch.name]["behind"] = len(compare_result_behind["commits"])
                cols[branch.name]["commits_summary"] = (
                    f"Behind: {cols[branch.name]['behind']}, Ahead: {cols[branch.name]['ahead']}"
                )
        return cols


class StGitlabProjectSnippetsListCommand(StGitlabProjectObjectsListCommand):
    @classmethod
    def shortcuts(cls) -> Dict[str, List[str]]:
        return {
            "open": ["Enter", "open"],
            "refresh": ["F5", "refresh"],
            "delete": ["Delete", "delete"],
            "ppage": [f"Shift+{left_arrow}", "prev. page"],
            "npage": [f"Shift+{right_arrow}", "next page"],
        }

    @classmethod
    def cols(cls) -> List[List[str]]:
        cols = [["open"], ["refresh", "delete"], ["ppage", "npage"]]
        return cols

    def get_objects(self) -> List[Snippet]:
        return self.gitlab.snippets(**self.query_params)

    def get_columns_properties(self) -> List[Dict[str, str]]:
        return utils.get_setting("snippets_list_columns", {})


class StGitlabUsersListCommand(StGitlabProjectObjectsListCommand):
    @classmethod
    def shortcuts(cls) -> Dict[str, List[str]]:
        return {
            "open": ["Enter", "open"],
            "refresh": ["F5", "refresh"],
            "ppage": [f"Shift+{left_arrow}", "prev. page"],
            "npage": [f"Shift+{right_arrow}", "next page"],
        }

    @classmethod
    def cols(cls) -> List[List[str]]:
        cols = [["open", "refresh"], ["ppage", "npage"]]
        return cols

    def get_objects(self) -> List[User]:
        users_group_filter = utils.get_setting("users_group_filter", [])
        if not users_group_filter:
            return self.gitlab.users(all=True, active=True)

        users: List[User] = []
        for group_name in users_group_filter:
            group = self.gitlab.group(group_name)
            if not group:
                continue
            users += group.members.list(active=True)

        return users

    def get_columns_properties(self) -> List[Dict[str, str]]:
        return utils.get_setting("users_list_columns", {})

    def special_cols(self) -> Dict[str, Any]:
        cols: Dict[str, Dict[str, Any]] = {}
        projects_filter = utils.get_setting("projects_filter", [])
        if projects_filter:
            projects = [self.gitlab.project(oid=pid) for pid in projects_filter]
        else:
            projects = self.gitlab.projects(all=True)

        for user in self.objects:
            issues_opened_cnt = sum([len(self.gitlab.issues(p.id, assignee_id=user.id, state="opened")) for p in projects])
            issues_closed_cnt = sum([len(self.gitlab.issues(p.id, assignee_id=user.id, state="closed")) for p in projects])
            merges_cnt = sum([len(self.gitlab.merges(p.id, assignee_id=user.id)) for p in projects])
            cols[user.id] = {}
            cols[user.id]["issues_ratio"] = f"{issues_opened_cnt}/{issues_closed_cnt}"
            cols[user.id]["merge_requests"] = f"{merges_cnt}"
        return cols
