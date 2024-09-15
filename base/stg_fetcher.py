#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

from __future__ import annotations
from typing import TYPE_CHECKING
import sublime  # type:ignore
import sublime_plugin  # type:ignore
from collections import OrderedDict

from tabulate import tabulate  # type:ignore

from . import utils
from .st_shortcuts_menu import StShortcutsMenu  # type:ignore
from .st_notes_icons import StNotesIcons  # type:ignore


if TYPE_CHECKING:
    from typing import List, Optional, Type, OrderedDict as TOrderedDict
    from ..libs.gitlab.base import RESTObject  # type: ignore
    from ..libs.gitlab.v4.objects import ProjectCommit  # type: ignore


BLOCK_LINE = "═" * 120
BLOCK_LINE_N = f"{BLOCK_LINE}\n"
MD_LINE = "─" * 119
BLOCK_MD_LINE_START = f"┌{MD_LINE}\n\n"
BLOCK_MD_LINE_STOP = f"└{MD_LINE}\n"


class StGitlabFetcherCommand(sublime_plugin.TextCommand):
    shortcuts: TOrderedDict[str, List[str]] = OrderedDict()
    cols: List[List[str]] = []
    obj_name = ""
    obj_name_sub = ""

    @classmethod
    def present(cls: Type["StGitlabFetcherCommand"], obj: RESTObject) -> str:
        cols_data = []
        cols_prop = f"{cls.obj_name_sub}_view_columns"
        cols = utils.get_setting(cols_prop, [])
        cols_present_prop = f"{cls.obj_name_sub}_view_columns_present"
        cols_present = utils.get_setting(cols_present_prop, [])
        char = utils.object_commands.get(cls.obj_name_sub, {}).get("char", "")

        for col in cols:
            if col["prop"] not in cols_present:
                continue

            value = utils.stg_get_property_value(obj, col)
            if value is None:
                continue

            value_name = col["colname"]
            value_char = char if col["prop"] in ["id", "iid"] else ""
            cols_data.append(f"{value_name}: {value_char}{value}")

        cols_data[1] = f"**{cols_data[1]}**"
        cols_data_print = " | ".join(cols_data)
        return f"* {cols_data_print}\n"

    def run(self, edit: sublime.Edit, obj_id: Optional[int] = None, project_id: Optional[int] = None) -> None:
        self.obj_id = obj_id if obj_id else self.view.settings().get("object_id")
        self.project_id = project_id if project_id else self.view.settings().get("project_id")

        self.validate_input()

        try:
            self.st_gitlab_view(edit)
        except Exception as e:
            self.view.window().status_message(f"{self.obj_name} #{obj_id} cannot be opened: {e}")

    def validate_input(self) -> None:
        if not self.obj_id:
            raise Exception(f"{self.obj_name} open failed - id is not defined")

        if not self.project_id:
            raise Exception(f"{self.obj_name} open failed - project is not defiened")

    def get_shortcuts(self, view: sublime.View) -> None:
        StShortcutsMenu(view, shortcuts=self.shortcuts, cols=self.cols)

    def get_title(self, obj: RESTObject) -> str:
        return obj.title

    def get_header(self, obj: RESTObject) -> str:
        header = ""
        header += f"## {self.get_title(obj)}\n"

        cols_prop = f"{self.obj_name_sub}_view_columns"
        cols = utils.get_setting(cols_prop, [])

        table_data = []
        if self.project_id:
            project = self.gitlab.project(self.project_id)
            table_data.append(["Project", project.name])

        col_labels = None
        max_len = 0
        for col in cols:
            if col["colname"] == "Project":
                # project name already added
                continue
            if col["colname"] == "Labels":
                col_labels = col
                continue

            if len(col["colname"]) > max_len:
                max_len = len(col["colname"])

            value = utils.stg_get_property_value(obj, col)

            if value is not None:
                # line = line_format.format(f"**{col['colname']}**", value)
                # cols_data.append(line)
                table_data.append([col["colname"], value])

        table = tabulate(
            table_data,
            tablefmt="rounded_outline",
        )
        header += table
        if col_labels is not None:
            header += "\n"
            header += BLOCK_LINE_N
            col_name = "Labels"
            offset_spcs = " " * (max_len - len(col_name))
            header += f"│ {col_name}{offset_spcs} │ {utils.stg_get_property_value(obj, col_labels)}"

        header += "\n"
        header += BLOCK_LINE_N
        return header

    def get_description(self, obj: RESTObject) -> Optional[str]:
        content = "## Description\n"
        content += BLOCK_MD_LINE_START
        descr = obj.description
        if not descr:
            return None
        else:
            descr = descr.replace("\r", "")
            content += f"{descr}\n\n"
        content += BLOCK_MD_LINE_STOP
        return content

    def get_object_custom(self, obj: RESTObject) -> str:
        return ""

    def note_commit(self, msg: str) -> str:
        MARKER = "mentioned in commit"
        commit_hash = None
        if MARKER in msg:
            commit_hash = msg.split(MARKER)[1].strip()

        if not commit_hash:
            return msg

        project = self.gitlab.project()
        if not project:
            return msg

        project_name = project.attributes.get("path_with_namespace")
        commit = self.gitlab.commit(sha=commit_hash[:8])
        if not commit:
            return msg

        msg_parts = msg.split(commit_hash)
        gl_url = utils.get_setting("gitlab_url").rstrip("/")
        url = f"{gl_url}/{project_name}/commit/{commit_hash[:8]}"
        return f"{msg_parts[0]} [{commit.title}]({url}) {msg_parts[-1]}"

    def get_notes(self, obj: RESTObject) -> str:
        """
        Show:
        * User notes
        * System notes
        * Label events
        """

        notes = ""
        content = ""
        notes_list = []
        if hasattr(obj, "notes"):
            notes_list = obj.notes.list(get_all=True)
        else:
            # Non-project snippet doesn't has a notes in API
            print("Warning: Object {} doesn't has a notes attribute".format(self.obj_name_sub))

        label_events = obj.resourcelabelevents.list()
        notes_list += label_events
        notes_list.sort(key=lambda x: x.created_at, reverse=False)
        is_show_systems_notes = utils.get_setting("show_system_notes")

        for note in notes_list:
            # Label Event
            if hasattr(note, "label") and hasattr(note, "action"):
                user = note.user.get("name", "")
                label_str = utils.stg_label_str(note.label["name"])
                action_str = "added" if note.action == "add" else "removed"
                msg = f"{action_str} label {label_str}"
                note_ts = utils.stg_get_datetime(note.created_at)
                notes += f"> {note.id}: {user} {msg} ({note_ts})\n"
                continue

            # Note
            note_attrs = note.attributes

            is_system = note_attrs.get("system", False)
            if is_system and not is_show_systems_notes:
                continue

            note_body = note_attrs.get("body", "").replace("\r", "")
            if not note_body:
                continue

            note_author = note_attrs.get("author", {}).get("name", "")
            note_ts = utils.stg_get_datetime(note_attrs.get("created_at"))

            if is_system:
                msg = utils.stg_msg_labels(note_body, obj.project_id)
                msg = self.note_commit(msg)
                notes += f"> {note.id}: {note_author} {msg} ({note_ts})\n"
                continue

            # User note
            notes += f"\n### Note:{note.id} by {note_author}\n"
            notes += BLOCK_MD_LINE_START
            notes += f"{note_body}\n"
            notes += "\n"
            notes += BLOCK_MD_LINE_STOP
            notes += f"*{note_ts}*\n\n"

        if notes:
            content += "## Notes\n\n"
            content += notes
        return content.replace("\n\n\n", "\n\n")

    def screen_name(self) -> str:
        return f"st_gitlab_{self.obj_name_sub}"

    def set_view_settings(self, view: sublime.View) -> None:
        screen = self.screen_name()
        view.settings().set("object_id", self.obj_id)
        view.settings().set("project_id", self.project_id)
        view.settings().set("screen", screen)
        view.settings().set("object_name", self.obj_name_sub)
        view.settings().set("st_gitlab_unselectable", True)
        view.set_name(f"{self.obj_name} #{self.obj_id}")

    def st_gitlab_view(self, edit: sublime.Edit) -> None:
        obj_current_id = self.view.settings().get("object_id")

        if obj_current_id == self.obj_id:
            r = self.view
            r.set_read_only(False)
            r.erase(edit, sublime.Region(0, self.view.size()))
        else:
            r = sublime.active_window().new_file()
            r.set_scratch(True)
            syntax_file = utils.get_setting("syntax_file")
            r.set_syntax_file(syntax_file)

        self.gitlab = utils.gl.get(r)  # creates with current view => r
        self.set_view_settings(r)
        obj = self.gitlab.object_by_view()
        if obj is None:
            return

        header_print = self.get_header(obj)
        self.get_shortcuts(r)
        description_print = self.get_description(obj)
        object_custom_print = self.get_object_custom(obj)
        notes_print = self.get_notes(obj)

        content = ""
        content += "\n"
        content += header_print
        if description_print:
            content += "\n"
            content += description_print
        if object_custom_print:
            content += "\n"
            content += object_custom_print
        if notes_print:
            content += "\n"
            content += notes_print

        r.run_command("st_gitlab_insert_text", {"position": 0, "text": content})
        r.show(0)
        StNotesIcons(r)
        sublime.set_timeout_async(utils.stg_show_images(r), 0)
        if self.project_id:
            r.run_command("st_gitlab_view_show_labels")
        r.set_read_only(True)


class StGitlabIssueFetcherCommand(StGitlabFetcherCommand):
    shortcuts = OrderedDict(
        [
            ("refresh", ["F5", "refresh"]),
            ("title", ["F2", "change title"]),
            ("branch", ["F7", "create branch"]),
            ("descr", ["d", "change description"]),
            ("addnote", ["c", "add note"]),
            ("chnote", ["Alt+c", "change note"]),
            ("state", ["s", "set state"]),
            ("setmile", ["m", "set milestone"]),
            ("labeladd", ["l", "label add"]),
            ("labeldel", ["Alt+l", "label remove"]),
            ("assign", ["a", "assing to"]),
            ("browser", ["g", "open in browser"]),
            ("move", ["p", "move to project"]),
            ("togglemode", ["Alt+u", "toggle select mode"]),
            ("togglenotes", ["Alt+r", "toggle system notes"]),
            ("openlink", ["w", "open link"]),
            ("change", ["Enter", "change"]),
            ("delete", ["Delete", "delete"]),
            ("toggletask", ["x", "toggle task"]),
        ]
    )

    cols = [
        ["refresh", "title", "descr", "state"],
        ["addnote", "labeladd", "setmile", "assign"],
        ["chnote", "labeldel", "togglemode", "togglenotes"],
        ["browser", "openlink", "move", "branch"],
        ["toggletask", "delete", "change"],
    ]

    obj_name = "Issue"
    obj_name_sub = "issue"

    def get_object_custom(self, obj: RESTObject) -> str:
        branches = self.gitlab.branches()
        content = ""
        if branches:
            content += "## Related branches\n"
            i = 1
            for br in branches:
                if not br.name.startswith(str(obj.iid)):
                    continue
                content += f"{i}. **{br.name}**: {br.commit.get('title')} by {br.commit.get('author_name')}\n"
        return content


class StGitlabMergeFetcherCommand(StGitlabFetcherCommand):
    shortcuts = OrderedDict(
        [
            ("refresh", ["F5", "refresh"]),
            ("title", ["F2", "change title"]),
            ("descr", ["d", "change description"]),
            ("addnote", ["c", "add note"]),
            ("chnote", ["Alt+c", "change note"]),
            ("state", ["s", "set state"]),
            ("setmile", ["m", "set milestone"]),
            ("labeladd", ["l", "label add"]),
            ("labeldel", ["Alt+l", "label remove"]),
            ("assign", ["a", "assing to"]),
            ("browser", ["g", "open in browser"]),
            ("wip", ["i", "toggle wip"]),
            ("togglemode", ["Alt+u", "toggle select mode"]),
            ("togglenotes", ["Alt+r", "toggle system notes"]),
            ("openlink", ["w", "open link"]),
            ("change", ["Enter", "change"]),
            ("accept", ["p", "accept"]),
            ("delete", ["Delete", "delete"]),
            ("toggletask", ["x", "toggle task"]),
        ]
    )

    cols = [
        ["refresh", "title", "descr", "state"],
        ["addnote", "labeladd", "setmile", "assign"],
        ["chnote", "labeldel", "togglemode", "togglenotes"],
        ["browser", "openlink", "wip", "accept", "delete"],
        ["toggletask", "change"],
    ]

    obj_name = "Merge-request"
    obj_name_sub = "merge"

    def get_object_custom(self, obj: RESTObject) -> str:
        project = self.gitlab.project()
        if project is None:
            return ""

        issues = obj.closes_issues()
        commits = obj.commits()
        # diffs = obj.diffs.list()
        content = ""
        if issues:
            content += "### Closes issues\n"
            for issue in issues:
                issue_content = StGitlabIssueFetcherCommand.present(issue)
                content += issue_content
                content += "\n"

        if commits:
            compare_result_ahead = project.repository_compare("master", obj.source_branch)
            compare_result_behind = project.repository_compare(obj.source_branch, "master")
            ahead = len(compare_result_ahead["commits"])
            behind = len(compare_result_behind["commits"])
            content += f"### Commits: {len(commits)} (branch: {obj.source_branch} - {behind} behind, {ahead} ahead)\n"

            for commit in commits:
                content += f"- By {commit.committer_name}: [{commit.title}]({self.get_commit_url(commit)})\n"
            content += "\n"
        else:
            commits = []

        # TODO: possib to show by click on commit in separate view
        # if diffs:
        #     content += '### Changes (%s)\n' % len(diffs)
        #     for diff in diffs:
        #         print(diff)
        #         d = obj.diffs.get(diff.id)
        #         print(d)
        #         for patch in d.diffs:
        #             content += BLOCK_MD_LINE_START
        #             content += '```diff\n'
        #             content += patch['diff']
        #             content += '```\n'
        #             content += BLOCK_MD_LINE_STOP

        branch_name = obj.attributes.get("source_branch")
        pipelines = self.gitlab.pipelines(ref=branch_name)
        if pipelines:
            content += "## Pipeline\n"
            pipeline_id = max([p.id for p in pipelines])
            pipeline = self.gitlab.pipeline(oid=pipeline_id)
            pipeline_content = StGitlabPipelineFetcherCommand.present(pipeline)
            content += pipeline_content
        return content

    def get_commit_url(self, commit: ProjectCommit) -> str:
        project = self.gitlab.project(oid=self.project_id)
        if project is None:
            return ""

        return f"{utils.get_setting('gitlab_url')}/{project.attributes.get('path_with_namespace')}/{commit.id}"

    def is_commit_in_merge(self, commits: List[ProjectCommit], commit_id: str) -> bool:
        for commit in commits:
            if commit_id == commit.id:
                return True
        return False


class StGitlabPipelineFetcherCommand(StGitlabFetcherCommand):
    shortcuts = OrderedDict(
        [
            ("refresh", ["F5", "refresh"]),
            ("retry", ["b", "retry"]),
            ("cancel", ["c", "cancel"]),
            ("browser", ["g", "open in browser"]),
            ("delete", ["Delete", "delete"]),
            ("togglemode", ["Alt+u", "toggle select mode"]),
        ]
    )

    cols = [["refresh"], ["retry"], ["cancel"], ["delete"], ["browser"], ["togglemode"]]

    obj_name = "Pipeline"
    obj_name_sub = "pipeline"

    def get_title(self, obj: RESTObject) -> str:
        return obj.attributes.get("ref", "")

    def get_description(self, obj: RESTObject) -> str:
        return ""

    def get_notes(self, obj: RESTObject) -> str:
        return ""

    def get_object_custom(self, obj: RESTObject) -> str:
        jobs = self.gitlab.jobs()
        if not jobs:
            return ""

        pipeline_jobs = [j for j in jobs if j.attributes.get("pipeline").get("id", None) == obj.id]
        content = ""
        if pipeline_jobs:
            content += "## Jobs\n"
            content += BLOCK_LINE_N
            for job in pipeline_jobs:
                if job.runner:
                    runner_name = job.runner.get("description", "<Uknown runner>")
                    content += f"* [ {job.status} ] {job.id} **{job.name}** on {runner_name}"
                else:
                    content += f"* [ {job.status} ] {job.id} **{job.name}**"

                content += "\n"
        return content


class StGitlabSnippetFetcherCommand(StGitlabFetcherCommand):
    shortcuts = OrderedDict(
        [
            ("refresh", ["F5", "refresh"]),
            ("title", ["F2", "change title"]),
            ("descr", ["d", "change description"]),
            ("chfile", ["f", "change snippet"]),
            ("addnote", ["c", "add note"]),
            ("chnote", ["Alt+c", "change note"]),
            ("browser", ["g", "open in browser"]),
            ("togglemode", ["Alt+u", "toggle select mode"]),
            ("togglenotes", ["Alt+r", "toggle system notes"]),
            ("openlink", ["w", "open link"]),
            ("change", ["Enter", "change"]),
            ("delete", ["Delete", "delete"]),
            ("toggletask", ["x", "toggle task"]),
        ]
    )

    cols = [
        ["refresh", "title", "descr"],
        ["addnote", "chfile"],
        ["chnote", "togglemode", "togglenotes"],
        ["browser", "openlink"],
        ["toggletask", "delete", "change"],
    ]

    obj_name = "Snippet"
    obj_name_sub = "snippet"

    def validate_input(self) -> None:
        if not self.obj_id:
            raise Exception(f"{self.obj_name} open failed - id is not defined")

    def auto_syntax(self, name: str) -> Optional[str]:
        return utils.syntaxes.get(name.split(".")[-1])

    def get_object_custom(self, obj: RESTObject) -> str:
        raw = obj.content()
        if not raw:
            return ""
        from io import BytesIO

        fp = BytesIO(raw)
        syntax_file = self.auto_syntax(obj.file_name)
        syntax_md = sublime.load_settings("SyntaxToMarkdown.sublime-settings")
        lang_md = syntax_md.get(syntax_file, "")
        content = f"## Snippet file preview: {obj.file_name}\n"
        content += BLOCK_MD_LINE_START
        content += f"```{lang_md}\n"
        content += fp.read().decode("utf-8").replace("\r", "")
        content += "\n```\n"
        content += BLOCK_MD_LINE_STOP
        content += "\n"
        return content
