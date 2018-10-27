#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

# import sublime
import sublime_plugin
from . import utils


class StGitlabObjectRemoveLabelCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        def on_done(i):
            if i < 0:
                return

            self.gitlab.label_del(obj_labels[i], obj)
            self.view.run_command('st_gitlab_object_refresh')

        self.gitlab = utils.gl.get()
        obj = self.gitlab.object_by_view()
        obj_labels = obj.attributes.get('labels', [])
        self.view.window().show_quick_panel(obj_labels, on_done)

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
