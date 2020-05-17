#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

# import sublime
import sublime_plugin
from . import utils
from .editbox import Editbox


class StGitlabObjectAddNoteCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        gitlab = utils.gl.get()
        project = gitlab.project()
        obj = gitlab.object_by_view()
        on_done = 'st_gitlab_object_add_note_done'
        eb = Editbox(self.view.id())
        eb.edit(
            'Note',
            on_done,
            '',
            project_id=project.id if project else None,
            object_id=obj.iid if hasattr(obj, 'iid') else obj.id
        )

    def is_visible(self, *args):
        screen = self.view.settings().get('screen')
        if not screen:
            return False
        valid_screens = [
            utils.object_commands.get('issue', {}).get('screen_view'),
            utils.object_commands.get('merge', {}).get('screen_view')
        ]
        if screen in valid_screens:
            return True
        return False


class StGitlabObjectAddNoteDoneCommand(sublime_plugin.TextCommand):
    def run(self, edit, text, obj_kwargs):
        gitlab = utils.gl.get(self.view)
        obj = gitlab.object_by_view()
        obj.notes.create({'body': text})
        self.view.run_command('st_gitlab_object_refresh')
