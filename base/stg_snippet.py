#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

import sublime
import sublime_plugin
from . import stg_utils as utils
from .stg_project import ProjectSelectPanel
from .stg_object import StGitlabObjectCommand


class StGitlabSnippetCreateCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        self.gitlab = utils.gl.get()
        self.project_id = self.view.settings().get('project_id', None)
        if self.project_id:
            self.set_project(self.project_id)
        else:
            panel = ProjectSelectPanel(callback=self.set_project)
            panel.show_input()

    def set_project(self, project_id):
        self.project_id = project_id
        self.project = self.gitlab.project(oid=self.project_id)
        self.get_snippet_title()

    def get_snippet_title(self):
        self.view.window().show_input_panel("New snippet title:", '', self.create_snippet, None, None)

    def create_snippet(self, title):
        snippet = self.project.snippets.create({'title': title})
        r = sublime.active_window().new_file()
        r.set_scratch(True)
        syntax_file = utils.stg_get_setting('syntax_file')
        r.set_syntax_file(syntax_file)
        r.settings().set('object_id', snippet.id)
        r.settings().set('project_id', self.project_id)
        r.run_command('st_gitlab_snippet_fetcher', {'obj_id': snippet.id})


class StGitlabSnippetCommand(StGitlabObjectCommand):

    INPUT_STR = 'Snippet ID'
    object_name = 'snippet'

    def get_issue(self):
        return self.gitlab.snippet(project_id=self.project_id, oid=self.obj_id)


class StGitlabSnippetDeleteCommand(StGitlabSnippetCommand):

    INPUT_STR = 'Snippet ID to delete'

    def refresh(self):
        if self.screen == 'st_gitlab_snippets':
            self.view.run_command('st_gitlab_project_list_refresh')
        elif self.screen == 'st_gitlab_snippet':
            self.view.close()

    def process(self):
        if not self.obj_id:
            return
        is_del = sublime.ok_cancel_dialog('Are you really want to delete snippet #%s?' % self.obj_id)
        if not is_del:
            return
        snippet = self.get_snippet()
        snippet.delete()
        self.refresh()

    def is_visible(self, *args):
        screen = self.view.settings().get('screen')
        if not screen:
            return False
        valid_screens = [
            utils.object_commands.get('snippet', {}).get('screen_view'),
            utils.object_commands.get('snippet', {}).get('screen_list')
        ]
        if screen in valid_screens:
            return True
        return False

