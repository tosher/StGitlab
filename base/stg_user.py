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
        users_menu = ['All users', 'Custom']
        self.users_group_filter = utils.get_setting('users_group_filter', [])
        if self.users_group_filter:
            users_menu[0] = 'All users (filtered)'

        self.window.show_quick_panel(users_menu, self.get_user)

    def get_user(self, idx):
        if idx < 0:
            return

        if idx == 0:
            if self.users_group_filter:
                users = utils.users_filtered(self.users_group_filter)
            else:
                users = utils.users_all()
            self.set_user(users)

        elif idx == 1:
            self.window.show_input_panel("User:", '', self.get_custom_user_done, None, None)

    def get_custom_user_done(self, user):
        if not user:
            return
        gitlab = utils.gl.get()
        users = [gitlab.user(name=user)]
        self.set_user(users)

    def set_user(self, users):
        self.user_names = []
        self.user_ids = []

        for user in users:
            if user.id not in self.user_ids:
                self.user_names.append(user.name)
                self.user_ids.append(user.id)

        if len(users) == 1:
            self.on_done(0)
        else:
            self.window.show_quick_panel(self.user_names, self.on_done)

    def on_done(self, idx):
        if idx < 0:
            return
        user_id = self.user_ids[idx]
        sublime.set_timeout_async(self.callback(user_id), 0)
