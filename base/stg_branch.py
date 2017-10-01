#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

# import sublime
from .stg_object import StGitlabObjectCommand
from . import stg_utils as utils


class StGitlabBranchCommand(StGitlabObjectCommand):

    INPUT_STR = 'Branch ID'
    object_name = 'branch'

    def get_branch(self):
        return self.gitlab.branch(project_id=self.project_id, oid=self.obj_id)

    def refresh(self):
        if self.screen == utils.object_commands.get('branch', {}).get('screen_list'):
            self.view.run_command('st_gitlab_project_list_refresh')
        # elif self.screen == utils.object_commands.get('branch', {}).get('screen_view'):
        #     self.view.run_command('st_gitlab_object_refresh')


class StGitlabBranchToggleProtectCommand(StGitlabBranchCommand):

    INPUT_STR = 'Branch'

    def process(self):
        if not self.obj_id:
            return

        br = self.get_branch()
        br.protect() if not br.protected else br.unprotect()
        self.refresh()

