#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

import re
import sublime
import sublime_plugin
from .base import *
from .base import stg_utils as utils
from .base.stg_html import StShortcutsMenu


class StGitlabInsertTextCommand(sublime_plugin.TextCommand):

    def run(self, edit, position, text):
        self.view.insert(edit, position, text)


# ### Events ###
class StGitlabLoad(sublime_plugin.EventListener):
    objects = ['issue', 'merge', 'pipeline', 'branch']

    def is_list_screen(self, view):
        for obj in self.objects:
            if view.settings().get('screen', None) == utils.object_commands.get(obj, {}).get('screen_list'):
                return True
            if view.settings().get('screen', None) == utils.object_commands.get(obj, {}).get('screen_board'):
                return True
        return False

    def is_unselectable(self, view):
        if self.is_list_screen(view):
            return True
        for obj in self.objects:
            if (view.settings().get('screen', None) == utils.object_commands.get(obj, {}).get('screen_view') and
                    view.settings().get('st_gitlab_unselectable', True)):
                return True
        return False

    def region_by_point(self, regions, point):
        for reg in regions:
            if reg.contains(point):
                return reg

    def select_table_column(self, view, forward):
        # TODO: cols: empty, empty, empty, non-empty (position is here)
        # move left => error
        line = view.line(view.sel()[0].end())
        line_text = view.substr(line)
        splitter = utils.stg_get_setting('table_column_separator')
        if not line_text.startswith(splitter):
            return False
        cols = line_text.split(splitter)[1:-1]
        regs = []
        point = line.a + 1
        for col in cols:
            reg = sublime.Region(point, point + len(col))
            point = reg.b + 1
            regs.append(reg)

        cursor = view.sel()[0].b
        if cursor > regs[-1].b:
            # cursor = regs[-1].b
            cursor = regs[0].a
        elif cursor < regs[0].a:
            cursor = regs[0].a
        while True:
            reg = self.region_by_point(regs, cursor)
            # NOTE: Switched off skipping of empty cols - check note upper
            # text = view.substr(reg)
            # if forward and not text.strip():
            #     cursor = reg.b + 1
            #     continue
            # elif forward is not None and not forward and not text.strip():
            #     cursor = reg.a - 1
            #     continue
            view.sel().clear()
            view.sel().add(reg)
            break
        return True

    def on_selection_modified(self, view):
        screen = view.settings().get('screen')
        if not screen or not screen.startswith('st_gitlab'):
            return

        if view.is_read_only() and self.is_unselectable(view):
            splitter = utils.stg_get_setting('table_column_separator')
            line = view.substr(view.line(view.sel()[0].end()))

            if view.settings().get('screen', '').endswith('board') and line.startswith(splitter):
                last_cmd = view.command_history(0)
                if last_cmd[0] == 'move' and last_cmd[1]['by'] == 'characters':
                    sel = view.sel()[0]
                    new_sel = sublime.Region(sel.a + 3, sel.b + 3) if last_cmd[1]['forward'] else sublime.Region(sel.a - 3, sel.b - 3)
                    view.sel().add(new_sel)
                    view.sel().subtract(sel)
                    forward = last_cmd[1]['forward']
                else:
                    forward = None
                if not self.select_table_column(view, forward):
                    view.sel().add(view.line(view.sel()[0].end()))
            else:
                view.sel().add(view.line(view.sel()[0].end()))


class StGitlabViewEvents(sublime_plugin.ViewEventListener):

    def on_query_context(self, key, operator, operand, match_all):
        if key == 'stg_screen':
            if operator == sublime.OP_EQUAL:
                if isinstance(operand, list):
                    return self.view.settings().get('screen', None) in operand
                else:
                    # print(key, operand, type(operand), operand == view.settings().get('screen', None))
                    return operand == self.view.settings().get('screen', None)
            if operator == sublime.OP_NOT_EQUAL:
                if isinstance(operand, list):
                    return self.view.settings().get('screen', None) not in operand
                else:
                    return operand != self.view.settings().get('screen', None)

    def on_activated_async(self):
        screen = self.view.settings().get('screen')
        if not screen or not screen.startswith('st_gitalb'):
            return
        if screen == utils.object_commands.get('issue', {}).get('screen_view'):
            StShortcutsMenu(
                self.view,
                shortcuts=StGitlabIssueFetcherCommand.shortcuts,
                cols=StGitlabIssueFetcherCommand.cols
            )
            StGitlabViewShowLabelsCommand.pretty_labels(self.view)
            utils.stg_show_images(self.view)
        elif screen == utils.object_commands.get('merge', {}).get('screen_view'):
            StShortcutsMenu(
                self.view,
                shortcuts=StGitlabMergeFetcherCommand.shortcuts,
                cols=StGitlabMergeFetcherCommand.cols
            )
            StGitlabViewShowLabelsCommand.pretty_labels(self.view)
            utils.stg_show_images(self.view)
        elif screen == utils.object_commands.get('pipeline', {}).get('screen_view'):
            StShortcutsMenu(
                self.view,
                shortcuts=StGitlabPipelineFetcherCommand.shortcuts,
                cols=StGitlabPipelineFetcherCommand.cols
            )
        elif screen == utils.object_commands.get('issue', {}).get('screen_list'):
            StShortcutsMenu(
                self.view,
                shortcuts=StGitlabProjectIssuesListCommand.shortcuts,
                cols=StGitlabProjectIssuesListCommand.cols
            )
        elif screen == utils.object_commands.get('merge', {}).get('screen_list'):
            StShortcutsMenu(
                self.view,
                shortcuts=StGitlabProjectMergesListCommand.shortcuts,
                cols=StGitlabProjectMergesListCommand.cols
            )
        elif screen == utils.object_commands.get('pipeline', {}).get('screen_list'):
            StShortcutsMenu(
                self.view,
                shortcuts=StGitlabProjectPipelinesListCommand.shortcuts,
                cols=StGitlabProjectPipelinesListCommand.cols
            )
        elif screen == utils.object_commands.get('branch', {}).get('screen_list'):
            StShortcutsMenu(
                self.view,
                shortcuts=StGitlabProjectBranchesListCommand.shortcuts,
                cols=StGitlabProjectBranchesListCommand.cols
            )

    def on_query_completions(self, prefix, locations):
        if self.view.settings().get('screen') == 'st_gitlab_editbox':
            gitlab = utils.gl.get()
            pattern_issue = re.compile(r'(^|.*\s)(\#)(\d+)?')
            completions = []
            cursor_position = locations[0]
            chars_before = self.view.substr(sublime.Region(cursor_position - 10, cursor_position))
            m = pattern_issue.match(chars_before)
            if m and m.group(2):
                issues = gitlab.issues()
                for issue in issues:
                    if m.group(3) and not str(issue.iid).startswith(m.group(3)):
                        continue
                    completions.append(('%s %s\tGitlab issue' % (issue.iid, issue.title), str(issue.iid)))
            if completions:
                return completions

            pattern_merge = re.compile(r'(^|.*\s)(\!)(\d+)?')
            m = pattern_merge.match(chars_before)
            if m and m.group(2):
                merges = gitlab.merges()
                for merge in merges:
                    if m.group(3) and not str(merge.iid).startswith(m.group(3)):
                        continue
                    completions.append(('%s %s\tGitlab merge-request' % (merge.iid, merge.title), str(merge.iid)))
            if completions:
                return completions

            pattern_user = re.compile(r'(^|.*\s)(\@)(\d+)?')
            m = pattern_user.match(chars_before)
            if m and m.group(2):
                users = gitlab.users()
                for user in users:
                    if m.group(3) and not user.name.startswith(m.group(3)):
                        continue
                    completions.append(('%s\tGitlab user' % user.name, user.name))
            if completions:
                return completions

        return []
