#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

from __future__ import annotations
from typing import TYPE_CHECKING
import sublime  # type:ignore

from . import utils

if TYPE_CHECKING:
    from typing import Callable, List, Optional
    from ..libs.gitlab.v4.objects import User  # type: ignore


class UserSelectPanel(object):
    def __init__(self, callback: Optional[Callable] = None):
        self.callback = callback
        self.window = sublime.active_window()

    def show_input(self) -> None:
        users_menu = ["All users", "Custom"]
        self.users_group_filter = utils.get_setting("users_group_filter", [])
        if self.users_group_filter:
            users_menu[0] = "All users (filtered)"

        self.window.show_quick_panel(users_menu, self.get_user)

    def get_user(self, idx: int) -> None:
        if idx < 0:
            return

        if idx == 0:
            if self.users_group_filter:
                users = utils.users_filtered(self.users_group_filter)
            else:
                users = utils.users_all()
            self.set_users(users)

        elif idx == 1:
            self.window.show_input_panel("User:", "", self.get_custom_user_done, None, None)

    def get_custom_user_done(self, user_name: str) -> None:
        if not user_name:
            return

        gitlab = utils.gl.get()
        users = [gitlab.user(name=user_name)]
        self.set_users(users)

    def set_users(self, users: List[User]) -> None:
        self.user_names: List[str] = []
        self.user_ids: List[int] = []

        for user in users:
            if user.id not in self.user_ids:
                self.user_names.append(user.name)
                self.user_ids.append(user.id)

        if len(users) == 1:
            self.on_done(0)
        else:
            self.window.show_quick_panel(self.user_names, self.on_done)

    def on_done(self, idx: int) -> None:
        if idx < 0:
            return
        user_id = self.user_ids[idx]

        if self.callback is None:
            return

        sublime.set_timeout_async(self.callback(user_id), 0)
