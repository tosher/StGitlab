#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

import sublime
import sublime_plugin
import traceback
# import textwrap
from . import stg_utils as utils
from .stg_gitlab import StGitlab

BLOCK_LINE = '%s\n' % ('═' * 80)
BLOCK_MD_LINE_START = '┌%s\n\n' % ('─' * 79)
BLOCK_MD_LINE_STOP = '└%s\n' % ('─' * 79)


class StGitlabFetcherCommand(sublime_plugin.TextCommand):

    shortcuts = []
    obj_name = ''
    obj_name_sub = ''

    def run(self, edit, obj_id):
        try:
            self.st_gitlab_view(edit, obj_id)
        except Exception as e:
            traceback.print_exc()
            sublime.status_message('%s #%s cannot be opened: %s' % (self.obj_name, obj_id, e))

    def get_shortcuts(self):
        shortcuts_print = ''
        maxlen = len(max(self.shortcuts, key=len)) + 2

        for idx, s in enumerate(self.shortcuts):
            idx += 1
            line_format = '{:<%s}\n' % (maxlen) if not idx % 5 else '{:<%s}' % maxlen
            shortcuts_print += line_format.format(s)
        return shortcuts_print

    def get_title(self, obj):
        return obj.title

    def get_header(self, obj):
        header = ''
        header += '## %s\n' % (self.get_title(obj))
        header += '\n'
        header += BLOCK_LINE

        cols_prop = '%s_view_columns' % self.obj_name_sub
        cols = utils.stg_get_setting(cols_prop, [])
        cols_maxlen = len(max([col['colname'] for col in cols], key=len)) + 5  # +4* +1
        cols_data = []
        line_format = '\t{:<%s}: {:<}' % cols_maxlen
        for col in cols:
            value = utils.stg_get_property_value(obj, col)

            if value is not None:
                line = line_format.format('**%s**' % col['colname'], value)
                cols_data.append(line)

        cols_data_print = '\n'.join(cols_data)
        header += cols_data_print
        return header

    def get_description(self, obj):
        content = '## Description\n'
        content += BLOCK_MD_LINE_START
        descr = obj.description
        if not descr:
            return None
        else:
            content += '%s\n\n' % descr.replace('\r', '')
        content += BLOCK_MD_LINE_STOP
        return content

    def get_object_custom(self, obj):
        return None

    def get_notes(self, obj):
        notes = ''
        content = ''
        # TODO: sorting not works?
        # for note in obj.notes.list(all=True, order_by='created_at', sort='desc'):
        # for note in reversed(obj.notes.list(all=True)):
        notes_list = obj.notes.list(all=True)
        notes_list.sort(key=lambda x: x.id, reverse=False)
        for note in notes_list:
            note_attrs = note.attributes
            is_full_notes_prop = '%s_show_full_notes' % self.obj_name_sub
            note_is_system = note_attrs.get('system', False)

            if not utils.stg_get_setting(is_full_notes_prop, True) and note_is_system:
                continue

            if note_attrs.get('body'):  # and not note.system:
                notes += '### Note:%s by %s\n' % (note.id, note_attrs.get('author', {}).get('name', ''))
                if not note_is_system:
                    notes += BLOCK_MD_LINE_START
                body = utils.stg_msg_labels(note_attrs.get('body', ''), obj.project_id)
                notes += '%s\n' % body.replace('\r', '')
                if not note_is_system:
                    notes += '\n'
                    notes += BLOCK_MD_LINE_STOP
                notes += '*(%s)*\n' % (utils.stg_get_datetime(note_attrs.get('created_at', None)))
        if notes:
            content += '## Notes\n'
            content += notes
        return content

    def obj_get(self, obj_id, project_id=None):
        return None

    def set_view_settings(self, view, obj_id, project_id):
        screen_prop_name = 'st_gitlab_%s' % self.obj_name_sub
        view.settings().set('object_id', obj_id)
        view.settings().set('project_id', project_id)
        view.settings().set('screen', screen_prop_name)
        view.settings().set('st_gitlab_unselectable', True)
        view.set_name('%s #%s' % (self.obj_name, obj_id))

    def st_gitlab_view(self, edit, obj_id):
        self.gitlab = StGitlab.connect()
        obj_current_id = self.view.settings().get('object_id', None)
        project_id = self.view.settings().get('project_id', None)

        if not project_id:
            raise Exception('Project is not defined. %s can not be opened.' % self.obj_name)

        if obj_current_id == obj_id:
            r = self.view
            r.set_read_only(False)
            r.erase(edit, sublime.Region(0, self.view.size()))
        else:
            r = sublime.active_window().new_file()
            r.set_scratch(True)
            syntax_file = utils.stg_get_setting('syntax_file')
            r.set_syntax_file(syntax_file)

        obj = self.obj_get(obj_id=obj_id, project_id=project_id)

        header_print = self.get_header(obj)
        shortcuts_print = self.get_shortcuts()
        description_print = self.get_description(obj)
        object_custom_print = self.get_object_custom(obj)
        notes_print = self.get_notes(obj)

        content = ''
        content += shortcuts_print
        content += '\n'
        content += '\n'
        content += header_print
        content += '\n'
        content += BLOCK_LINE
        if object_custom_print:
            content += '\n'
            content += object_custom_print
        if description_print:
            content += '\n'
            content += description_print
        if notes_print:
            content += '\n'
            content += notes_print

        r.insert(edit, 0, content)
        self.set_view_settings(r, obj_id, project_id)
        sublime.set_timeout_async(utils.stg_show_images(r), 0)
        r.run_command('st_gitlab_view_show_labels')
        r.set_read_only(True)


class StGitlabIssueFetcherCommand(StGitlabFetcherCommand):
    shortcuts = [
        '[r](refresh)',
        '[f2](change title)',
        '[d](change description)',
        '[c](add note)',
        '[s](change state)',
        '[v](change milestone)',
        '[j](label add)',
        '[k](label remove)',
        '[a](assing to)',
        '[g](open in browser)',
        '[m](move to project)',
        '[u](toggle select mode)',
        '[Enter](*change any)',
        '[Delete](delete)'
    ]
    obj_name = 'Issue'
    obj_name_sub = 'issue'

    def obj_get(self, obj_id, project_id):
        project = self.gitlab.projects.get(project_id)
        return project.issues.get(obj_id)


class StGitlabMergeFetcherCommand(StGitlabFetcherCommand):
    shortcuts = [
        '[r](refresh)',
        '[f2](change title)',
        '[d](change description)',
        '[c](add note)',
        '[s](change state)',
        '[v](change milestone)',
        '[j](label add)',
        '[k](label remove)',
        '[a](assing to)',
        '[g](open in browser)',
        '[u](toggle select mode)',
        '[Enter](*change any)'
    ]
    obj_name = 'Merge-request'
    obj_name_sub = 'merge'

    def obj_get(self, obj_id, project_id):
        project = self.gitlab.projects.get(project_id)
        return project.mergerequests.get(obj_id)

    def get_object_custom(self, obj):
        issues = obj.closes_issues()
        commits = obj.commits()
        if issues or commits:
            content = '## Data\n'
            content += BLOCK_LINE
        if issues:
            content += '### Closes issues\n'
            for issue in issues:
                content += '#%s **%s**\n' % (issue.iid, issue.title)
        if commits:
            content += '\n### Commits\n'
            for commit in commits:
                content += '- **%s** by %s, id:%s\n' % (commit.title, commit.committer_name, commit.short_id)
            content += BLOCK_LINE
        return content


class StGitlabPipelineFetcherCommand(StGitlabFetcherCommand):
    shortcuts = [
        '[r](refresh)',
        '[b](retry)',
        '[c](cancel)',
        '[g](open in browser)',
        '[u](toggle select mode)',
        '[Enter](*magic)'
    ]
    obj_name = 'Pipeline'
    obj_name_sub = 'pipeline'

    def obj_get(self, obj_id, project_id):
        project = self.gitlab.projects.get(project_id)
        return project.pipelines.get(obj_id)

    def get_title(self, obj):
        return obj.attributes.get('ref', '')

    def get_description(self, obj):
        return ''

    def get_notes(self, obj):
        return ''
