#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

import sublime
import sublime_plugin
from . import stg_utils as utils
from .stg_gitlab import StGitlab


class StGitlabPipelineCommand(sublime_plugin.TextCommand):

    INPUT_STR = 'Pipeline ID'

    def run(self, edit, obj_id=None):
        self.screen = self.view.settings().get('screen', None)
        if not obj_id:
            if self.screen == 'st_gitlab_pipelines':
                colsep = utils.stg_get_setting('table_column_separator')
                line = self.view.substr(self.view.line(self.view.sel()[0].end()))
                obj_id = line.split(colsep)[1].strip()
            elif self.screen == 'st_gitlab_pipeline':
                obj_id = self.view.settings().get('object_id', None)

        if not obj_id:
            self.view.window().show_input_panel(self.INPUT_STR, '', self.process, None, None)
        else:
            self.process(obj_id)

    def get_pipeline(self, obj_id):
        project_id = self.view.settings().get('project_id', None)
        gitlab = StGitlab.connect()
        project = gitlab.projects.get(project_id)
        return project.pipelines.get(obj_id)

    def refresh(self):
        if self.screen == 'st_gitlab_pipelines':
            self.view.run_command('st_gitlab_project_list_refresh')
        elif self.screen == 'st_gitlab_pipeline':
            self.view.run_command('st_gitlab_object_refresh', {'object_name': 'pipeline'})

    def process(self, obj_id):
        if not obj_id:
            return
        self.view.run_command('st_gitlab_pipeline_fetcher', {'obj_id': obj_id})


class StGitlabPipelineCancelCommand(StGitlabPipelineCommand):

    INPUT_STR = 'Pipeline ID to cancel'

    def process(self, obj_id):
        if not obj_id:
            return
        is_cancel = sublime.ok_cancel_dialog('Are you really want to cancel pipeline #%s?' % obj_id)
        if not is_cancel:
            return
        pl = self.get_pipeline(obj_id)
        pl.cancel()
        self.refresh()


class StGitlabPipelineRetryCommand(StGitlabPipelineCommand):

    INPUT_STR = 'Pipeline ID to retry'

    def process(self, obj_id):
        if not obj_id:
            return
        is_cancel = sublime.ok_cancel_dialog('Are you want to retry pipeline #%s?' % obj_id)
        if not is_cancel:
            return
        pl = self.get_pipeline(obj_id)
        pl.retry()
        self.refresh()
