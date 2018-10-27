#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

import sublime
import sublime_plugin
from . import utils


class StGitlabObjectCheckBoxToggleCommand(sublime_plugin.TextCommand):
    MARKDOWN_SCOPE = 'text.html.markdown.gfm'
    LINES_COUNT_BETWEEN_HEADER_AND_TEXT_START = 3  # TODO: bad way!

    def run(self, edit):
        gitlab = utils.gl.get()
        self.obj = gitlab.object_by_view()
        header_pattern = r'^#{2,3}\s.*$'
        selected_header_str = ''
        try:
            headers = []
            headers_all = self.view.find_all(header_pattern)
            for h in headers_all:
                if self.MARKDOWN_SCOPE not in self.view.scope_name(h.a):
                    headers.append(h)
            selected = self.view.sel()[0]
            selected_header = max([h for h in headers if h.b < selected.b])
            selected_header_str = self.view.substr(selected_header).lstrip('# ')
        except Exception as e:
            print(e)

        if selected_header_str:
            header_line = self.view.rowcol(selected_header.a)[0]
            edit_line = self.view.rowcol(self.view.sel()[0].a)[0]
            checkbox_line = edit_line - header_line - self.LINES_COUNT_BETWEEN_HEADER_AND_TEXT_START
            if selected_header_str.startswith('Description'):
                self.toogle_checkbox_description(linenum=checkbox_line)
            elif selected_header_str.startswith('Note:'):
                note_id = selected_header_str.split()[0].split(':')[-1]
                self.toogle_checkbox_note(linenum=checkbox_line, note_id=note_id)

    # NOTE: linenum start from 0, not from 1!
    def toggle_line(self, lines, linenum):
        success = False
        line = lines[linenum]
        if ' [ ]' in line:
            line = line.replace(' [ ]', ' [x]')
            success = True
        elif ' [x]' in line:
            line = line.replace(' [x]', ' [ ]')
            success = True
        if success:
            lines[linenum] = line
        return lines, success

    def toogle_checkbox_description(self, linenum):
        description = self.obj.description
        lines = description.split('\n')
        lines, success = self.toggle_line(lines, linenum)
        if success:
            self.obj.description = '\n'.join(lines)
            self.obj.save()
            self.view.run_command('st_gitlab_object_refresh')

    def toogle_checkbox_note(self, linenum, note_id):
        note = self.obj.notes.get(note_id)
        if note.attributes.get('system', False):
            sublime.message_dialog("Unable to edit system message.")
            return

        body = note.body
        lines = body.split('\n')
        lines, success = self.toggle_line(lines, linenum)
        if success:
            note.body = '\n'.join(lines)
            note.save()
            self.view.run_command('st_gitlab_object_refresh')

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
