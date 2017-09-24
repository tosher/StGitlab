#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

import sublime
from .stg_object import StGitlabObjectCommand


class StGitlabPipelineCommand(StGitlabObjectCommand):

    INPUT_STR = 'Pipeline ID'
    SCREEN_LIST = 'st_gitlab_pipelines'
    SCREEN_VIEW = 'st_gitlab_pipeline'
    FETCHER = 'st_gitlab_pipeline_fetcher'

    def get_pipeline(self):
        return self.gitlab.pipeline(project_id=self.project_id, oid=self.obj_id)

    def refresh(self):
        if self.screen == 'st_gitlab_pipelines':
            self.view.run_command('st_gitlab_project_list_refresh')
        elif self.screen == 'st_gitlab_pipeline':
            self.view.run_command('st_gitlab_object_refresh', {'object_name': 'pipeline'})


class StGitlabPipelineCancelCommand(StGitlabPipelineCommand):

    INPUT_STR = 'Pipeline ID to cancel'

    def process(self, obj_id):
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
