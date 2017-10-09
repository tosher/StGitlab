#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

import sublime
import sublime_plugin
from . import stg_utils as utils
from .stg_editbox import StEditbox


class StGitlabObjectChangeNoteCommand(sublime_plugin.TextCommand):

    def run(self, edit, note_id):
        if not note_id:
            return
        gitlab = utils.gl.get()
        project = gitlab.project()
        obj = gitlab.object_by_view()
        note = obj.notes.get(note_id)
        if note.attributes.get('system', False):
            sublime.message_dialog("Unable to edit system message.")
            return
        on_done = 'st_gitlab_object_change_note_done'
        eb = StEditbox(self.view.id())
        eb.edit(
            'Note %s' % note_id,
            on_done,
            note.attributes.get('body', ''),
            project_id=project.id,
            object_id=obj.iid,
            note_id=note_id
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


class StGitlabObjectChangeNoteDoneCommand(sublime_plugin.TextCommand):
    def run(self, edit, text):
        base_id = self.view.settings().get('base_id')
        note_id = self.view.settings().get('note_id')
        eb = StEditbox(base_id)
        eb.layout_base()
        gitlab = utils.gl.get(eb.view)
        obj = gitlab.object_by_view()
        note = obj.notes.get(note_id)
        note.body = text
        note.save()
        eb.view.run_command('st_gitlab_object_refresh')
