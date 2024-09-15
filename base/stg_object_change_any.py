#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

import sublime  # type: ignore

from . import utils
from .stg_object import StGitlabObjectTextCommand


class StGitlabObjectChangeAnyCommand(StGitlabObjectTextCommand):
    VALID_SCREENS = {
        "issue": ["screen_view"],
        "merge": ["screen_view"],
        "pipeline": ["screen_view"],
    }

    MARKDOWN_SCOPE = "text.html.markdown.gfm"

    def run(self, edit: sublime.Edit) -> None:
        object_name = self.view.settings().get("object_name")
        header_pattern = r"^#{1,3}\s.*$"
        selected = self.view.sel()[0]
        selected_header_str = ""
        headers = []
        try:
            headers_all = self.view.find_all(header_pattern)
            for h in headers_all:
                if self.MARKDOWN_SCOPE not in self.view.scope_name(h.a):
                    headers.append(h)
            selected_header = max([h for h in headers if h.b <= selected.b])
            selected_header_str = self.view.substr(selected_header).lstrip("# ")
        except Exception as e:
            sublime.active_window().status_message(f"Property change failed, error while selecting: {e}")
            return

        if selected_header_str:
            if selected_header_str.startswith("Description"):
                self.view.run_command("st_gitlab_object_change_description")
            elif selected_header_str.startswith("Note:"):
                note_id = selected_header_str.split()[0].split(":")[-1]
                self.view.run_command("st_gitlab_object_change_note", {"note_id": note_id})
            elif selected_header_str.startswith("Notes"):
                self.view.run_command("st_gitlab_object_add_note")
            elif selected_header_str.startswith("Snippet file"):
                self.view.run_command("st_gitlab_snippet_change_file")
            else:
                cols = utils.get_setting(f"{object_name}_view_columns", [])
                colname = ""
                tokens = self.view.substr(selected).split("│")
                if len(tokens) > 1:
                    colname = tokens[1].strip()

                if not colname and selected_header.a == 1 and selected.a <= selected_header.a and selected.b >= selected_header.b:
                    # First header - title, inside selection
                    self.view.run_command("st_gitlab_object_change_title")
                    return

                col_prop = ""
                for col in cols:
                    if colname != col["colname"]:
                        continue

                    col_prop = col["prop"]
                    if col_prop == "iid":
                        self.view.run_command("st_gitlab_object_in_browser")
                    elif col_prop == "title":
                        self.view.run_command("st_gitlab_object_change_title")
                    elif col_prop == "milestone":
                        self.view.run_command("st_gitlab_object_set_milestone")
                    elif col_prop == "state":
                        self.view.run_command("st_gitlab_object_change_state")
                    elif col_prop == "project":
                        self.view.run_command("st_gitlab_change_project")
                    elif col_prop == "assignee":
                        self.view.run_command("st_gitlab_object_change_assigned")
                    elif col_prop == "labels":
                        self.view.run_command("st_gitlab_object_add_label")
                    else:
                        sublime.message_dialog("Not implemented in this version")
