#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

# import sublime
import sublime_plugin


class StGitlabToggleSelectableCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        is_unselectable = self.view.settings().get('st_gitlab_unselectable', True)
        if is_unselectable:
            self.view.settings().set('st_gitlab_unselectable', False)
        else:
            self.view.settings().set('st_gitlab_unselectable', True)
