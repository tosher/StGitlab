#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

import sublime
import sublime_plugin
from . import stg_utils as utils


class StGitlabMergeAcceptCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        gitlab = utils.gl.get()
        project = gitlab.project()
        merge = gitlab.merge()
        if project and merge:
            if merge.merge_status != 'can_be_merged':
                sublime.message_dialog('There are merge conflicts. Merge-request can not be accepted.')
                return
            merge.merge()
        self.view.run_command('st_gitlab_object_refresh')

    def is_visible(self, *args):
        screen = self.view.settings().get('screen')
        if not screen:
            return False
        valid_screens = [
            utils.object_commands.get('merge', {}).get('screen_view')
        ]
        if screen in valid_screens:
            return True
        return False


