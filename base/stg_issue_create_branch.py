#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

import sys
import os
# import sublime
import sublime_plugin
from . import utils
sys.path.append(os.path.join(os.path.dirname(__file__), "../libs"))
from transliterate import translit


class StGitlabIssueCreateBranchCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        def on_done(name):
            if not name:
                return
            project.branches.create({'branch': name, 'ref': 'master'})
            self.view.run_command('st_gitlab_object_refresh')

        gitlab = utils.gl.get()
        project = gitlab.project()
        self.issue = gitlab.issue()
        branch_name = '%s-%s' % (self.issue.iid, self.get_branch_name())
        if project and self.issue:
            self.view.window().show_input_panel("Title:", branch_name, on_done, None, None)

    def get_branch_name(self):
        translit_lang = utils.get_setting('issue_to_branch_transliterate_lang')
        if not translit_lang:
            return ''
        return (
            translit(self.issue.title, translit_lang, reversed=True)
            .replace("'", '')
            .replace('.', '')
            .replace(' ', '-')
        )

    def is_visible(self, *args):
        screen = self.view.settings().get('screen')
        if not screen:
            return False
        valid_screens = [
            utils.object_commands.get('issue', {}).get('screen_view')
        ]
        if screen in valid_screens:
            return True
        return False

