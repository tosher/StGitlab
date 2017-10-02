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
        return False

    def is_unselectable(self, view):
        if self.is_list_screen(view):
            return True
        for obj in self.objects:
            if (view.settings().get('screen', None) == utils.object_commands.get(obj, {}).get('screen_view') and
                    view.settings().get('st_gitlab_unselectable', True)):
                return True
        return False

    def on_selection_modified(self, view):
        if view.is_read_only() and self.is_unselectable(view):
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
        if not screen:
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
                    completions.append(('%s %s' % (issue.iid, issue.title), str(issue.iid)))
            if completions:
                return completions

            pattern_merge = re.compile(r'(^|.*\s)(\!)(\d+)?')
            m = pattern_merge.match(chars_before)
            if m and m.group(2):
                merges = gitlab.merges()
                for merge in merges:
                    if m.group(3) and not str(merge.iid).startswith(m.group(3)):
                        continue
                    completions.append(('%s %s' % (merge.iid, merge.title), str(merge.iid)))
            if completions:
                return completions

        return []
