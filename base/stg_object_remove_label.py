#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

# import sublime
import sublime_plugin
from . import stg_utils as utils
from .stg_gitlab import StGitlab


# Issue remove label
class StGitlabRemoveLabelCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        def on_done(i):
            if i < 0:
                return

            if object_id:
                obj_labels.remove(obj_labels[i])
                obj.save(labels=','.join(obj_labels))
                self.object_refresh()

        self.validate()

        gitlab = StGitlab.connect()
        object_id = self.get_object_id()
        project_id = self.get_project_id()
        if object_id:
            self.project = gitlab.projects.get(project_id)
            obj = self.get_object(object_id)
            obj_labels = obj.attributes.get('labels', [])
            self.view.window().show_quick_panel(obj_labels, on_done)

    def validate(self):
        pass

    def get_object_id(self):
        return None

    def get_project_id(self):
        return self.view.settings().get('project_id', None)

    def get_object(self, object_id):
        return None

    def object_refresh(self):
        return None


class StGitlabIssueRemoveLabelCommand(StGitlabRemoveLabelCommand):

    def validate(self):
        utils.stg_validate_screen('st_gitlab_issue')

    def get_object_id(self):
        return self.view.settings().get('object_id', None)

    def get_object(self, object_id):
        return self.project.issues.get(object_id)

    def object_refresh(self):
        self.view.run_command('st_gitlab_object_refresh', {'object_name': 'issue'})


class StGitlabMergeRemoveLabelCommand(StGitlabRemoveLabelCommand):

    def validate(self):
        utils.stg_validate_screen('st_gitlab_merge')

    def get_object_id(self):
        return self.view.settings().get('object_id', None)

    def get_object(self, object_id):
        return self.project.mergerequests.get(object_id)

    def object_refresh(self):
        self.view.run_command('st_gitlab_object_refresh', {'object_name': 'merge'})
