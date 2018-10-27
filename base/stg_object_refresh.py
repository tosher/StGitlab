#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

# import sublime
import sublime_plugin
from . import utils


class StGitlabObjectRefreshCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        cursor = self.view.sel()[0]
        object_name = self.view.settings().get('object_name', None)
        object_id = self.view.settings().get('object_id', None)
        if object_id and object_name:
            self.view.erase_phantoms('shortcuts')
            self.view.erase_phantoms('label')
            cmd = utils.object_commands.get(object_name, {}).get('fetch')
            self.view.run_command(cmd, {'obj_id': object_id})
            self.view.sel().clear()
            self.view.sel().add(cursor)
            self.view.show(cursor)

    def is_visible(self, *args):
        screen = self.view.settings().get('screen')
        if not screen:
            return False
        valid_screens = [
            utils.object_commands.get('issue', {}).get('screen_view'),
            utils.object_commands.get('merge', {}).get('screen_view'),
            utils.object_commands.get('pipeline', {}).get('screen_view')
        ]
        if screen in valid_screens:
            return True
        return False
