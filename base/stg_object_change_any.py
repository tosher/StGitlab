#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

import sublime
import sublime_plugin
from . import stg_utils as utils
# from .stg_gitlab import StGitlab


class StGitlabObjectChangeAnyCommand(sublime_plugin.TextCommand):
    def run(self, edit):

        utils.stg_validate_screen(
            [
                'st_gitlab_issue',
                'st_gitlab_merge',
                'st_gitlab_pipeline'
            ]
        )

        screen = self.view.settings().get('screen', None)
        if screen == 'st_gitlab_issue':
            object_name = 'issue'
        elif screen == 'st_gitlab_merge':
            object_name = 'merge'
        elif screen == 'st_gitlab_pipeline':
            object_name = 'pipeline'

        is_unselectable = self.view.settings().get('st_gitlab_unselectable', True)
        if not is_unselectable:
            self.view.settings().set('st_gitlab_unselectable', True)
            self.view.sel().add(self.view.line(self.view.sel()[0].end()))

        # header_pattern = '^##\s.*$'
        header_pattern = '^#{2,3}\s.*$'
        selected_header_str = ''
        try:
            headers = self.view.find_all(header_pattern)
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
                print(note_id)
                self.view.run_command('st_gitlab_object_change_note', {'note_id': note_id})
            elif selected_header_str.startswith('Notes'):
                self.view.run_command('st_gitlab_object_add_note')
            else:
                cols = utils.stg_get_setting('%s_view_columns' % object_name, [])
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
                            self.view.run_command('st_gitlab_%s_go' % object_name)
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
                            self.view.run_command('st_gitlab_%s_add_label' % object_name)
                        else:
                            sublime.message_dialog('Not implemented in this version')
