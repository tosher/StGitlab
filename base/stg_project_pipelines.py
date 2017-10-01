#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

# import sublime
import sublime_plugin
from . import stg_utils as utils
from .stg_project import ProjectSelectPanel


# Issues by project
class StGitlabProjectPipelinesCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        panel = ProjectSelectPanel(callback=self.get_pipelines)
        panel.show_input()

    def get_pipelines(self, project_id):
        gitlab = utils.gl.get()
        project = gitlab.project(oid=project_id)
        per_page = utils.stg_get_setting('list_page_size')
        query_params = {
            'project_id': project_id,
            'page': 1,
            'per_page': per_page
        }
        title = 'Pipelines: %s' % project.name
        r = self.view.window().new_file()
        r.set_name(title)
        syntax_file = utils.stg_get_setting('syntax_file')
        r.set_syntax_file(syntax_file)
        r.settings().set('query_params', query_params)
        r.settings().set('screen', utils.object_commands.get('pipeline', {}).get('screen_list'))
        r.settings().set('object_name', 'pipeline')
        r.settings().set("word_wrap", False)
        r.settings().set("project_id", project_id)
        cmd = utils.object_commands.get('pipeline', {}).get('list')
        r.run_command(cmd, {'title': title})
        r.set_scratch(True)
        # r.run_command('st_gitlab_view_show_labels')
        r.set_read_only(True)

