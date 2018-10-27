#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

import sublime
import sublime_plugin
from . import utils


class StGitlabObjectChangeAnyCommand(sublime_plugin.TextCommand):
    MARKDOWN_SCOPE = 'text.html.markdown.gfm'

    def run(self, edit):
        object_name = self.view.settings().get('object_name', None)
        # is_unselectable = self.view.settings().get('st_gitlab_unselectable', True)
        # if not is_unselectable:
        #     self.view.settings().set('st_gitlab_unselectable', True)
        #     self.view.sel().add(self.view.line(self.view.sel()[0].end()))

        # header_pattern = '^##\s.*$'
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
            if selected_header_str.startswith('Description'):
                self.view.run_command('st_gitlab_object_change_description')
            elif selected_header_str.startswith('Note:'):
                note_id = selected_header_str.split()[0].split(':')[-1]
                self.view.run_command('st_gitlab_object_change_note', {'note_id': note_id})
            elif selected_header_str.startswith('Notes'):
                self.view.run_command('st_gitlab_object_add_note')
            elif selected_header_str.startswith('Snippet file'):
                self.view.run_command('st_gitlab_snippet_change_file')
            else:
                cols = utils.get_setting('%s_view_columns' % object_name, [])
                try:
                    colname = self.view.substr(selected).split('**')[1]
                except Exception as e:
                    print('Enter fire exception: %s' % e)
                    colname = ''

                col_prop = ''
                for col in cols:
                    if colname == col['colname']:
                        col_prop = col['prop']
                        if col_prop == 'iid':
                            self.view.run_command('st_gitlab_object_in_browser')
                        elif col_prop == 'title':
                            self.view.run_command('st_gitlab_object_change_title')
                        elif col_prop == 'milestone':
                            self.view.run_command('st_gitlab_object_set_milestone')
                        elif col_prop == 'state':
                            self.view.run_command('st_gitlab_object_change_state')
                        elif col_prop == 'project':
                            self.view.run_command('st_gitlab_change_project')
                        elif col_prop == 'assignee':
                            self.view.run_command('st_gitlab_object_change_assigned')
                        elif col_prop == 'labels':
                            self.view.run_command('st_gitlab_object_add_label')
                        else:
                            sublime.message_dialog('Not implemented in this version')

    def is_visible(self, *args):
        screen = self.view.settings().get('screen')
        if not screen:
            return False
        valid_screens = [
            utils.object_commands.get('issue', {}).get('screen_view'),
            utils.object_commands.get('merge', {}).get('screen_view'),
            utils.object_commands.get('pipeline', {}).get('screen_view')
        ]
        if screen in valid_screens:
            return True
        return False

