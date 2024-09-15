#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

import sublime  # type:ignore

from . import utils
from .stg_object import StGitlabObjectTextCommand


class StGitlabObjectSetMilestoneCommand(StGitlabObjectTextCommand):
    VALID_SCREENS = {
        "issue": ["screen_view"],
        "merge": ["screen_view"],
    }

    def run(self, edit: sublime.Edit) -> None:
        def on_done(index: int) -> None:
            if index < 0:
                return
            if index == 0:
                gitlab.milestone_del(obj)
            else:
                oid = milestones[index - 1].id
                gitlab.milestone_set(oid, obj)
            self.view.run_command("st_gitlab_object_refresh")

        gitlab = utils.gl.get()
        milestones_menu = ["[Remove]"]
        obj = gitlab.object_by_view()
        # milestones = gitlab.milestones(state='active')
        milestones = gitlab.milestones(all=True)

        if milestones is not None:
            for mile in milestones:
                milestones_menu.append(mile.title)
            sublime.set_timeout(lambda: sublime.active_window().show_quick_panel(milestones_menu, on_done), 1)
