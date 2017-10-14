#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

import sublime
import sublime_plugin
from . import stg_utils as utils


class StGitlabEditboxSaveCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        text = self.view.substr(sublime.Region(0, self.view.size()))
        cmd = self.view.settings().get('on_done')
        self.view.run_command(cmd, {'text': text})

    def is_visible(self, *args):
        screen = self.view.settings().get('screen')
        if not screen:
            return False
        if screen in ['st_gitlab_editbox']:
            return True
        return False


class StGitlabEditboxCancelCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        is_del = sublime.ok_cancel_dialog('Are you really want to cancel editing?')
        if not is_del:
            return
        base_id = self.view.settings().get('base_id')
        eb = StEditbox(base_id)
        eb.layout_base()

    def is_visible(self, *args):
        screen = self.view.settings().get('screen')
        if not screen:
            return False
        if screen in ['st_gitlab_editbox']:
            return True
        return False


class StEditbox(object):
    CELL_MAIN = [0, 0, 1, 1]  # group of base view
    CELL_EDIT = [0, 1, 1, 2]  # group of editor
    CELL_MAIN_GROUP = 0  # index of base group in cells of layout
    CELL_EDIT_GROUP = 1  # index of editor group in cells of layout

    def __init__(self, base_id, syntax_auto=False, height=None):
        self.base_id = base_id
        self.view = self.view_base()
        self.window = self.view.window()
        self.syntax_auto = syntax_auto
        self.height = height

    def edit(self, title, on_done, text=None, **kwargs):
        if not text:
            text = ''
        self.layout_edit()
        self.editbox = self.window.new_file()
        self.editbox.set_name(title)
        self.editbox.set_scratch(True)
        if not self.syntax_auto:
            syntax_file = utils.stg_get_setting('syntax_file_edit')
            self.editbox.set_syntax_file(syntax_file)
        else:
            syntax_file = self.auto_syntax(title)
            if syntax_file:
                self.editbox.set_syntax_file(syntax_file)
        self.editbox.settings().set('on_done', on_done)
        self.editbox.settings().set('base_id', self.base_id)
        self.editbox.settings().set('screen', 'st_gitlab_editbox')
        self.editbox.settings().set("word_wrap", True)
        for arg in kwargs.keys():
            self.editbox.settings().set(arg, kwargs[arg])
        self.editbox.run_command('st_gitlab_insert_text', {'position': 0, 'text': text})

    def auto_syntax(self, name):
        return utils.syntaxes.get(name.split('.')[-1])

    def layout(self):
        return self.window.layout()

    def is_active(self):
        lt = self.layout()
        action = True if len(lt.get('cells', [])) > 1 else False
        return action

    def focus_editbox(self):
        if self.is_active():
            self.window.focus_group(self.CELL_EDIT_GROUP)

    def view_base(self):
        views = sublime.active_window().views_in_group(self.CELL_MAIN_GROUP)
        for view in views:
            if view.id() == self.base_id:
                return view

    def view_editbox(self):
        if self.is_active():
            return sublime.active_window().views_in_group(self.CELL_EDIT_GROUP)[0]
        return None

    def focus_base(self):
        self.window.focus_group(self.CELL_MAIN_GROUP)

    def get_editbox_height(self):
        h = self.height if self.height else utils.stg_get_setting('edit_height_percent')

        ratio = (100 - int(h)) / 100
        return ratio

    def layout_edit(self):
        r = self.get_editbox_height()
        self.window.run_command(
            'set_layout',
            {
                "cols": [0.0, 1.0],
                "rows": [0.0, r, 1.0],
                "cells": [
                    self.CELL_MAIN,
                    self.CELL_EDIT
                ]
            }
        )
        self.focus_editbox()

    def layout_base(self):
        self.view_editbox().close()
        self.focus_base()
        self.window.run_command(
            'set_layout',
            {
                "cols": [0.0, 1.0],
                "rows": [0.0, 1.0],
                "cells": [
                    self.CELL_MAIN
                ]
            }
        )
