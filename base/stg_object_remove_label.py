#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

# import sublime
import sublime_plugin
from . import stg_utils as utils


class StGitlabObjectRemoveLabelCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        def on_done(i):
            if i < 0:
                return

            self.gitlab.label_del(obj_labels[i], obj)
            self.view.run_command('st_gitlab_object_refresh')

        utils.stg_validate_screen(
            [
                'st_gitlab_issue',
                'st_gitlab_merge'
            ]
        )

        self.gitlab = utils.gl.get()
        obj = self.gitlab.object_by_view()
        obj_labels = obj.attributes.get('labels', [])
        self.view.window().show_quick_panel(obj_labels, on_done)
