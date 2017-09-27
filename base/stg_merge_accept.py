#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

# import sublime
import sublime_plugin
from . import stg_utils as utils


class StGitlabMergeAcceptCommand(sublime_plugin.TextCommand):
    def run(self, edit):

        utils.stg_validate_screen('st_gitlab_merge')

        gitlab = utils.gl.get()
        project = gitlab.project()
        merge = gitlab.merge()
        if project and merge:
            merge.merge()
        self.view.run_command('st_gitlab_object_refresh', {'object_name': 'merge'})


