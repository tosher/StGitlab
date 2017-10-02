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


class StGitlabBranchCreateMergeCommand(StGitlabBranchCommand):
    INPUT_STR = 'Branch'

    def process(self):
        def on_done(name):
            if not name:
                return
            project = self.gitlab.project(oid=self.project_id)
            project.mergerequests.create({
                'source_branch': branch.name,
                'target_branch': 'master',
                'title': name,
                'description': description
            })
            self.refresh()

        if not self.obj_id:
            return

        branch = self.get_branch()
        issue_id = None
        try:
            issue_id = int(branch.name.split('-')[0])
            issue = self.gitlab.issue(oid=issue_id)
            title = 'Resolve: %s' % issue.title
            description = 'Closes #%s\n' % issue_id
        except Exception:
            issue = None
            title = ''
            description = ''

        self.view.window().show_input_panel("Title:", title, on_done, None, None)
