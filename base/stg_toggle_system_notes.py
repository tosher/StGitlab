#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

# import sublime
import sublime_plugin
from . import utils


class StGitlabToggleSystemNotesCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        is_show_system_notes = utils.get_setting('show_system_notes')
        if is_show_system_notes:
            utils.set_setting('show_system_notes', False)
        else:
            utils.set_setting('show_system_notes', True)
        self.view.run_command('st_gitlab_object_refresh')

    def is_visible(self, *args):
        screen = self.view.settings().get('screen')
        if not screen:
            return False
        if screen in ['st_gitlab_issue', 'st_gitlab_merge']:
            return True
        return False
