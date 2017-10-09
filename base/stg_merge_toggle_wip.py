#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

import re
# import sublime
import sublime_plugin
from . import stg_utils as utils


class StGitlabMergeToggleWipCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        gitlab = utils.gl.get()
        project = gitlab.project()
        merge = gitlab.merge()
        if project and merge:
            val = False if merge.attributes.get('work_in_progress') else True
            title = merge.attributes.get('title')
            title = 'WIP:%s' % title if val else re.sub(r'^wip[:\s]', '', title, flags=re.IGNORECASE)
            merge.save(title=title)
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


