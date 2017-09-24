#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

import sublime
import sublime_plugin
from . import stg_utils as utils
from .stg_gitlab import StGitlab
from .stg_editbox import StEditbox


class StGitlabObjectChangeNoteCommand(sublime_plugin.TextCommand):

    def run(self, edit, note_id):
        if not note_id:
            return

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


class StGitlabObjectChangeNoteDoneCommand(sublime_plugin.TextCommand):
    def run(self, edit, text):
        gitlab = StGitlab()
        base_id = self.view.settings().get('base_id')
        note_id = self.view.settings().get('note_id')
        eb = StEditbox(base_id)
        eb.layout_base()
        screen = eb.view.settings().get('screen')
        obj = gitlab.object_by_screen(screen)
        note = obj.notes.get(note_id)
        note.body = text
        note.save()
        eb.view.run_command('st_gitlab_object_refresh', {'object_name': gitlab.object_name_by_screen(screen)})
