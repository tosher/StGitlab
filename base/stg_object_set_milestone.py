#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

import sublime
import sublime_plugin
from . import stg_utils as utils


class StGitlabObjectSetMilestoneCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        def on_done(index):
            if index < 0:
                return
            if index == 0:
                gitlab.milestone_del(obj)
            else:
                oid = milestones[index - 1].id
                gitlab.milestone_set(oid, obj)
            self.view.run_command('st_gitlab_object_refresh')

        gitlab = utils.gl.get()
        milestones_menu = ['[Remove]']
        obj = gitlab.object_by_view()
        # milestones = gitlab.milestones(state='active')
        milestones = gitlab.milestones(all=True)

        if milestones is not None:
            for mile in milestones:
                milestones_menu.append(mile.title)
            sublime.set_timeout(lambda: sublime.active_window().show_quick_panel(milestones_menu, on_done), 1)

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
