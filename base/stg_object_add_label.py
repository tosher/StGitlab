#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

# import sublime
import sublime_plugin
from . import stg_utils as utils


class StGitlabAddLabelCommand(sublime_plugin.TextCommand):

    SCREEN_VALIDATE = ''
    OBJECT_NAME = ''

    def run(self, edit, object_id=None):
        def on_done(i):
            if i < 0:
                return

            obj_labels.append(labels_names[i])
            obj.save(labels=','.join(obj_labels))
            self.object_refresh()

        self.validate()
        self.object_id = object_id
        self.gitlab = utils.gl.get()
        obj = self.get_object()
        obj_labels = obj.attributes.get('labels', [])
        labels = self.gitlab.labels(all=True)
        labels_names = [lab.name for lab in labels if lab.name not in obj_labels]
        self.view.window().show_quick_panel(labels_names, on_done)

    def validate(self):
        utils.stg_validate_screen(self.SCREEN_VALIDATE)

    def get_object(self):
        return None

    def object_refresh(self):
        self.view.run_command('st_gitlab_object_refresh', {'object_name': self.OBJECT_NAME})


class StGitlabIssueAddLabelCommand(StGitlabAddLabelCommand):

    SCREEN_VALIDATE = 'st_gitlab_issue'
    OBJECT_NAME = 'issue'

    def get_object(self):
        return self.gitlab.issue(oid=self.object_id)


class StGitlabMergeAddLabelCommand(StGitlabAddLabelCommand):

    SCREEN_VALIDATE = 'st_gitlab_merge'
    OBJECT_NAME = 'merge'

    def get_object(self):
        return self.gitlab.merge(oid=self.object_id)
