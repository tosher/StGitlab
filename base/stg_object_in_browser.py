#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

# import sublime
import webbrowser
import sublime_plugin
from . import stg_utils as utils


# Issue: Open in Browser
class StGitlabObjectInBrowserCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        gitlab = utils.gl.get()
        project = gitlab.project()
        screen = self.view.settings().get('screen', None)
        if screen == 'st_gitlab_issue':
            obj = gitlab.issue()
            web_url = obj.attributes.get('web_url')
        elif screen == 'st_gitlab_merge':
            obj = gitlab.merge()
            web_url = obj.attributes.get('web_url')
        elif screen == 'st_gitlab_pipeline':
            # url not exists in api now
            obj = gitlab.pipeline()
            web_url = '%(url)s/%(project)s/pipelines/%(pid)s' % {
                'url': utils.stg_get_setting('gitlab_url'),
                'project': project.attributes.get('path_with_namespace'),
                'pid': obj.id
            }
        webbrowser.open(web_url)

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
