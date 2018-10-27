#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

from io import BytesIO
# import sublime
import sublime_plugin
from . import utils
from .editbox import Editbox


class StGitlabSnippetChangeFileCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        gitlab = utils.gl.get()
        project = gitlab.project()
        obj = gitlab.object_by_view()
        raw = obj.content()
        fp = BytesIO(raw)
        text = fp.read().decode('utf-8').replace('\r', '')
        on_done = 'st_gitlab_snippet_change_file_done'
        eb = Editbox(self.view.id(), syntax_auto=True, height=80)
        eb.edit(
            obj.file_name,
            on_done,
            text,
            project_id=project.id,
            object_id=obj.iid if hasattr(obj, 'iid') else obj.id
        )

    def is_visible(self, *args):
        screen = self.view.settings().get('screen')
        if not screen:
            return False
        valid_screens = [
            utils.object_commands.get('snippet', {}).get('screen_view')
        ]
        if screen in valid_screens:
            return True
        return False


class StGitlabSnippetChangeFileDoneCommand(sublime_plugin.TextCommand):
    def run(self, edit, text, obj_kwargs):
        gitlab = utils.gl.get(self.view)
        obj = gitlab.object_by_view()
        # obj.save(code=text)
        obj.code = text
        obj.save()
        self.view.run_command('st_gitlab_object_refresh')
