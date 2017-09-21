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

        object_id = self.view.settings().get('object_id', None)
        project_id = self.view.settings().get('project_id', None)
        if object_id and project_id:
            screen = self.view.settings().get('screen', None)
            gitlab = StGitlab.connect()
            project = gitlab.projects.get(project_id)
            if screen == 'st_gitlab_issue':
                obj = project.issues.get(object_id)
                web_url = obj.attributes.get('web_url')
            elif screen == 'st_gitlab_merge':
                obj = project.mergerequests.get(object_id)
                web_url = obj.attributes.get('web_url')
            elif screen == 'st_gitlab_pipeline':
                # url not exists in api now
                # obj = project.pipelines.get(object_id)
                web_url = '%s/%s/pipelines/%s' % (
                    utils.stg_get_setting('gitlab_url'),
                    project.attributes.get('path_with_namespace'),
                    object_id
                )
            webbrowser.open(web_url)
