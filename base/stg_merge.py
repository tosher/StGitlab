#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

import sublime_plugin
from . import stg_utils as utils
# from .stg_gitlab import StGitlab


# View Merge-request
class StGitlabMergeCommand(sublime_plugin.TextCommand):
    def run(self, edit, obj_id=None):
        if not obj_id:
            colsep = utils.stg_get_setting('table_column_separator')
            try:
                line = self.view.substr(self.view.line(self.view.sel()[0].end()))
                obj_id = line.split(colsep)[1].strip()
                int(obj_id)  # check is number
            except Exception as e:
                print('Exception: %s' % e)
                pass

        if not obj_id:
            obj_id = ''
            self.view.window().show_input_panel("Merge-request ID#:", obj_id, self.get_merge, None, None)
        else:
            self.get_merge(obj_id)

    def get_merge(self, text):
        self.view.run_command('st_gitlab_merge_fetcher', {'obj_id': text})
