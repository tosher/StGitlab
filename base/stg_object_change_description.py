#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

# import sublime
import sublime_plugin
from . import stg_utils as utils
from .stg_editbox import StEditbox


class StGitlabObjectChangeDescriptionCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        utils.stg_validate_screen(
            [
                'st_gitlab_issue',
                'st_gitlab_merge'
            ]
        )

        gitlab = utils.gl.get()
        project = gitlab.project()
        obj = gitlab.object_by_view()
        on_done = 'st_gitlab_object_change_description_done'
        description = obj.description if obj.description else ''
        eb = StEditbox(self.view.id())
        eb.edit(
            'Description',
            on_done,
            description,
            project_id=project.id,
            object_id=obj.iid
        )


class StGitlabObjectChangeDescriptionDoneCommand(sublime_plugin.TextCommand):
    def run(self, edit, text):
        base_id = self.view.settings().get('base_id')
        eb = StEditbox(base_id)
        eb.layout_base()
        gitlab = utils.gl.get(eb.view)
        obj = gitlab.object_by_view()
        obj.description = text
        obj.save()
        eb.view.run_command('st_gitlab_object_refresh')
