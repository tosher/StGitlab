#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

# import sublime
import sublime_plugin
from . import stg_utils as utils
from .stg_gitlab import StGitlab
from .stg_editbox import StEditbox


class StGitlabObjectChangeDescriptionCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        utils.stg_validate_screen(
            [
                'st_gitlab_issue',
                'st_gitlab_merge'
            ]
        )

        gitlab = StGitlab()
        screen = self.view.settings().get('screen', None)
        project = gitlab.project()
        if screen == 'st_gitlab_issue':
            obj = gitlab.issue()
        elif screen == 'st_gitlab_merge':
            obj = gitlab.merge()
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
        gitlab = StGitlab()
        base_id = self.view.settings().get('base_id')
        eb = StEditbox(base_id)
        eb.layout_base()
        screen = eb.view.settings().get('screen')
        obj = gitlab.object_by_screen(screen)
        obj.description = text
        obj.save()
        eb.view.run_command('st_gitlab_object_refresh', {'object_name': gitlab.object_name_by_screen(screen)})
