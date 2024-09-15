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
    import sublime  # type:ignore
    from ..libs.gitlab.v4.objects import ProjectBoard, Issue  # type: ignore

left_arrow = utils.get_setting("char_left_arrow")
right_arrow = utils.get_setting("char_right_arrow")


class StGitlabProjectIssuesBoardDrawCommand(sublime_plugin.TextCommand):
    shortcuts = {
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

    cols = [
        ["open", "refresh", "new"],
        ["labeladd", "mileset", "assigneeset"],
        ["labeldel", "miledel", "assigneedel"],
        ["filter", "ppage", "npage"],
    ]

    def run(self, edit: sublime.Edit, title: str) -> None:
        self.title = title
        self.query_params = self.view.settings().get("query_params", {})
        self.gitlab = utils.gl.get()
        self.board = self.get_board()
        self.labels = self.gitlab.labels(all=True)
        self.labels_backlog = self.get_backlog_labels()
        self.build()

    def build(self) -> None:
        self.show_shortcuts()
        content = "\n"
        content += self.show_header()
        content += self.show_filters()
        content += self.show_table()
        self.view.run_command("st_gitlab_insert_text", {"position": 0, "text": content})
        self.view.show(0)

    def show_shortcuts(self) -> None:
        StShortcutsMenu(self.view, shortcuts=self.shortcuts, cols=self.cols)

    def show_header(self) -> str:
        header = "\n"
        header += f"## {self.title}\n"
        page = self.query_params.get("page")
        per_page = self.query_params.get("per_page")
        header += f"\t**Page number**: {page} ({per_page} issues per page)\n"
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

    def get_board(self) -> ProjectBoard:
        return self.gitlab.boards()[0]

    def get_backlog_labels(self) -> List[str]:
        lists_labels = []
        lists = self.board.attributes.get("lists", [])
        for li in lists:
            lists_labels.append(self.list_label(li))
        return [lbl.name for lbl in self.labels if lbl.name not in lists_labels]

    def get_issues_backlog(self) -> List[Issue]:
        blabels = self.get_backlog_labels()
        issues = []
        for lab in blabels:
            issues += self.gitlab.issues(labels=[lab], state="opened")
        return list(set(issues))

    def get_issues_closed(self) -> List[Issue]:
        return self.gitlab.issues(state="closed")

    def get_issues_list(self, li: Dict[str, Any]) -> List[Issue]:
        return self.gitlab.issues(labels=[self.list_label(li)], state="opened")

    def list_label(self, li: Dict[str, Any]) -> str:
        return li.get("label", {}).get("name")

    # def get_columns_properties(self):
    #     return utils.get_setting('issue_list_columns', {})

    # TODO: issue with important & in_progress: which list?
    def show_table(self) -> str:
        max_width = 35
        tbl_header = ["Backlog"] + [self.list_label(li) for li in self.board.attributes.get("lists", [])] + ["Closed"]
        table_data = []

        by_cols = []
        by_cols.append(self.get_issues_backlog())
        for li in self.board.attributes.get("lists", []):
            li_issues = self.get_issues_list(li)
            by_cols.append(li_issues)
        by_cols.append(self.get_issues_closed())

        lines_cnt = len(max(by_cols, key=len))
        for linenum in range(lines_cnt):
            table_line = []
            for col in by_cols:
                if len(col) >= linenum + 1:
                    issue_str = f"{col[linenum].iid}: {col[linenum].title}"
                    table_line.append(utils.stg_cut(issue_str, max_width))
                else:
                    table_line.append("")
            table_data.append(table_line)

        table = tabulate(
            table_data,
            tablefmt="rounded_outline",
            headers=tbl_header,
        )
        return table
