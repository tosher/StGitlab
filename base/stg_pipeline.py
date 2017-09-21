#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

import sublime
import sublime_plugin
from . import stg_utils as utils
from .stg_gitlab import StGitlab


# View pipeline
class StGitlabPipelineCommand(sublime_plugin.TextCommand):
    def run(self, edit, obj_id=None):
        if not obj_id:
            colsep = utils.stg_get_setting('table_column_separator')
            try:
                line = self.view.substr(self.view.line(self.view.sel()[0].end()))
                obj_id = line.split(colsep)[1].strip()
                int(obj_id)
            except Exception as e:
                print('Exception: %s' % e)
                pass

        if not obj_id:
            obj_id = ''
            self.view.window().show_input_panel("Pipeline ID#:", obj_id, self.get_pipeline, None, None)
        else:
            self.get_pipeline(obj_id)

    def get_pipeline(self, text):
        self.view.run_command('st_gitlab_pipeline_fetcher', {'obj_id': text})


class StGitlabPipelineCancelCommand(sublime_plugin.TextCommand):
    def run(self, edit, obj_id=None):
        if not obj_id:
            colsep = utils.stg_get_setting('table_column_separator')
            try:
                line = self.view.substr(self.view.line(self.view.sel()[0].end()))
                obj_id = line.split(colsep)[1].strip()
                int(obj_id)
            except Exception as e:
                print('Exception: %s' % e)
                pass

        if not obj_id:
            obj_id = ''
            self.view.window().show_input_panel("Pipeline ID to cancel:", obj_id, self.pipeline_cancel, None, None)
        else:
            self.get_pipeline(obj_id)

    def pipeline_cancel(self, obj_id):
        if not obj_id:
            return
        is_cancel = sublime.ok_cancel_dialog('Are you really want to cancel pipeline #%s?' % obj_id)
        if not is_cancel:
            return
        project_id = self.view.settings().get('project_id', None)
        gitlab = StGitlab.connect()
        project = gitlab.projects.get(project_id)
        pl = project.pipelines.get(obj_id)
        pl.cancel()


class StGitlabPipelineRetryCommand(sublime_plugin.TextCommand):
    def run(self, edit, obj_id=None):
        if not obj_id:
            colsep = utils.stg_get_setting('table_column_separator')
            try:
                line = self.view.substr(self.view.line(self.view.sel()[0].end()))
                obj_id = line.split(colsep)[1].strip()
                int(obj_id)
            except Exception as e:
                print('Exception: %s' % e)
                pass

        if not obj_id:
            obj_id = ''
            self.view.window().show_input_panel("Pipeline ID to cancel:", obj_id, self.pipeline_cancel, None, None)
        else:
            self.get_pipeline(obj_id)

    def pipeline_cancel(self, obj_id):
        if not obj_id:
            return
        is_cancel = sublime.ok_cancel_dialog('Are you want to retry pipeline #%s?' % obj_id)
        if not is_cancel:
            return
        project_id = self.view.settings().get('project_id', None)
        gitlab = StGitlab.connect()
        project = gitlab.projects.get(project_id)
        pl = project.pipelines.get(obj_id)
        pl.retry()
        if self.view.settings().get('screen', None) == 'st_gitlab_pipelines':
            self.view.run_command('st_gitlab_list_refresh')


