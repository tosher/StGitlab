#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

# import sublime
import sublime_plugin
from . import stg_utils as utils


class StGitlabObjectChangeTitleCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        def on_done(text):
            if text is not None:
                obj.title = text
                obj.save()
                self.view.run_command('st_gitlab_object_refresh')

        utils.stg_validate_screen(
            [
                'st_gitlab_issue',
                'st_gitlab_merge'
            ]
        )

        gitlab = utils.gl.get()
        obj = gitlab.object_by_view()
        self.view.window().show_input_panel("Title:", obj.title, on_done, None, None)
