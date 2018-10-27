#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

import sublime
# import sublime_plugin
from . import utils


class UserSelectPanel(object):

    def __init__(self, callback=None):
        self.callback = callback
        self.window = sublime.active_window()

    def show_input(self):
        self.user_names = []
        self.user_ids = []

        users_group_filter = utils.get_setting('users_group_filter', [])
        if users_group_filter:
            users = utils.users_filtered(users_group_filter)
        else:
            users = utils.users_all()

        for user in users:
            if user.id not in self.user_ids:
                self.user_names.append(user.name)
                self.user_ids.append(user.id)

        # if users_group_filter:
        #     groups_lists = [gitlab.group(group).members.list(active=True) for group in users_group_filter]
        #     for gr_users in groups_lists:
        #         for user in gr_users:
        #             if user.id not in self.user_ids:
        #                 self.user_names.append(user.name)
        #                 self.user_ids.append(user.id)
        # else:
        #     users = gitlab.users(all=True, active=True)
        #     self.user_names = []
        #     self.user_ids = []
        #     for user in users:
        #         self.user_names.append(user.name)
        #         self.user_ids.append(user.id)

        self.window.show_quick_panel(self.user_names, self.on_done)

    def on_done(self, idx):
        if idx < 0:
            return
        user_id = self.user_ids[idx]
        sublime.set_timeout_async(self.callback(user_id), 0)

