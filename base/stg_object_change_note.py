#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

import sublime
import sublime_plugin
from . import utils
from .editbox import Editbox


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
        eb = Editbox(self.view.id())
        eb.edit(
            'Note %s' % note_id,
            on_done,
            note.attributes.get('body', ''),
            project_id=project.id,
            object_id=obj.iid if hasattr(obj, 'iid') else obj.id,
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
    def run(self, edit, text, obj_kwargs):
        if obj_kwargs is None:
            raise Exception('Note arguments is empty')

        note_id = obj_kwargs.get('note_id')
        gitlab = utils.gl.get(self.view)
        obj = gitlab.object_by_view()
        note = obj.notes.get(note_id)
        if not hasattr(note, 'save'):
            sublime.message_dialog('Sorry, note save for %s is not implemened in Python Gitlab API.' % obj.__class__.__name__)
            return
        note.body = text
        note.save()
        self.view.run_command('st_gitlab_object_refresh')
