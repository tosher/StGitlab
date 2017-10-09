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

        gitlab = utils.gl.get()
        obj = gitlab.object_by_view()
        self.view.window().show_input_panel("Title:", obj.title, on_done, None, None)

    def is_visible(self, *args):
        screen = self.view.settings().get('screen')
        if not screen:
            return False
        valid_screens = [
            utils.object_commands.get('issue', {}).get('screen_view'),
            utils.object_commands.get('merge', {}).get('screen_view')
        ]
        if screen in valid_screens:
            return True
        return False
