#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

import sublime
from .stg_object import StGitlabObjectCommand
from . import stg_utils as utils


class StGitlabPipelineCommand(StGitlabObjectCommand):

    INPUT_STR = 'Pipeline ID'
    object_name = 'pipeline'

    def get_pipeline(self):
        return self.gitlab.pipeline(project_id=self.project_id, oid=self.obj_id)

    def refresh(self):
        if self.screen == utils.object_commands.get('pipeline', {}).get('screen_list'):
            self.view.run_command('st_gitlab_project_list_refresh')
        elif self.screen == utils.object_commands.get('pipeline', {}).get('screen_view'):
            self.view.run_command('st_gitlab_object_refresh')


class StGitlabPipelineCancelCommand(StGitlabPipelineCommand):

    INPUT_STR = 'Pipeline ID to cancel'

    def process(self):
        if not self.obj_id:
            return
        is_cancel = sublime.ok_cancel_dialog('Are you really want to cancel pipeline #%s?' % self.obj_id)
        if not is_cancel:
            return
        pl = self.get_pipeline()
        pl.cancel()
        self.refresh()


class StGitlabPipelineRetryCommand(StGitlabPipelineCommand):

    INPUT_STR = 'Pipeline ID to retry'

    def process(self):
        if not self.obj_id:
            return
        is_cancel = sublime.ok_cancel_dialog('Are you want to retry pipeline #%s?' % self.obj_id)
        if not is_cancel:
            return
        pl = self.get_pipeline()
        pl.retry()
        self.refresh()
