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

    def is_visible(self, *args):
        screen = self.view.settings().get('screen')
        if not screen:
            return False
        if screen in ['st_gitlab_issue', 'st_gitlab_merge', 'st_gitlab_pipeline']:
            return True
        return False
