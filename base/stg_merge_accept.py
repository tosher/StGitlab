#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

import sublime  # type: ignore

from . import utils
from .stg_object import StGitlabObjectTextCommand


class StGitlabMergeAcceptCommand(StGitlabObjectTextCommand):
    VALID_SCREENS = {
        "merge": ["screen_view"],
    }

    def run(self, edit: sublime.Edit) -> None:
        gitlab = utils.gl.get()
        project = gitlab.project()
        merge = gitlab.merge()
        if project and merge:
            if merge.merge_status != "can_be_merged":
                sublime.message_dialog("There are merge conflicts. Merge-request can not be accepted.")
                return
            merge.merge()
        self.view.run_command("st_gitlab_object_refresh")
