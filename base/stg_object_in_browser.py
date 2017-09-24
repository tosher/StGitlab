#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

# import sublime
import webbrowser
import sublime_plugin
from . import stg_utils as utils
from .stg_gitlab import StGitlab


# Issue: Open in Browser
class StGitlabObjectInBrowserCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        utils.stg_validate_screen(
            [
                'st_gitlab_issue',
                'st_gitlab_merge',
                'st_gitlab_pipeline'
            ]
        )

        gitlab = StGitlab()
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
