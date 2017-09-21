#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

import sublime
import sublime_plugin
from .base import *


class StGitlabInsertTextCommand(sublime_plugin.TextCommand):

    def run(self, edit, position, text):
        self.view.insert(edit, position, text)


# ### Events ###
class StGitlabLoad(sublime_plugin.EventListener):
    objects = ['issue', 'merge', 'pipeline']

    def is_list_screen(self, view):
        for obj in self.objects:
            if view.settings().get('screen', None) == 'st_gitlab_%ss' % obj:
                return True
        return False

    def is_unselectable(self, view):
        if self.is_list_screen(view):
            return True
        for obj in self.objects:
            if view.settings().get('screen', None) == 'st_gitlab_%s' % obj and view.settings().get('st_gitlab_unselectable', True):
                return True
        return False

    def on_selection_modified(self, view):
        if view.is_read_only() and self.is_unselectable(view):
            view.sel().add(view.line(view.sel()[0].end()))


class StGitlabViewEvents(sublime_plugin.EventListener):

    def on_query_context(self, view, key, operator, operand, match_all):
        if key == 'stg_screen':
            if operator == sublime.OP_EQUAL:
                if isinstance(operand, list):
                    return view.settings().get('screen', None) in operand
                else:
                    # print(key, operand, type(operand), operand == view.settings().get('screen', None))
                    return operand == view.settings().get('screen', None)
            if operator == sublime.OP_NOT_EQUAL:
                if isinstance(operand, list):
                    return view.settings().get('screen', None) not in operand
                else:
                    return operand != view.settings().get('screen', None)

