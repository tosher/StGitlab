#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

import sublime
import sublime_plugin


class StGitlabObjectRefreshCommand(sublime_plugin.TextCommand):
    def run(self, edit, object_name):
        object_id = self.view.settings().get('object_id', None)
        if object_id:
            self.view.erase_phantoms('label')
            self.view.run_command('st_gitlab_%s_fetcher' % object_name, {'obj_id': object_id})
            sublime.status_message('%s was refreshed!' % object_name.title())
