#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

# import sublime
import sublime_plugin
from . import stg_utils as utils


class StGitlabToggleSystemNotesCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        is_show_system_notes = utils.stg_get_setting('show_system_notes')
        if is_show_system_notes:
            utils.stg_set_setting('show_system_notes', False)
        else:
            utils.stg_set_setting('show_system_notes', True)
        gitlab = utils.gl.get()
        screen = self.view.settings().get('screen')
        self.view.run_command('st_gitlab_object_refresh', {'object_name': gitlab.object_name_by_screen(screen)})
