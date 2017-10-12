#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

import sublime
import sublime_plugin
from collections import OrderedDict
import traceback
# import textwrap
from . import stg_utils as utils
from .stg_html import StShortcutsMenu

BLOCK_LINE = '%s\n' % ('═' * 80)
BLOCK_MD_LINE_START = '┌%s\n\n' % ('─' * 79)
BLOCK_MD_LINE_STOP = '└%s\n' % ('─' * 79)


class StGitlabFetcherCommand(sublime_plugin.TextCommand):

    shortcuts = []
    cols = None
    obj_name = ''
    obj_name_sub = ''

    @classmethod
    def present(cls, obj):
        cols_data = []
        cols_prop = '%s_view_columns' % cls.obj_name_sub
        cols = utils.stg_get_setting(cols_prop, [])
        cols_present_prop = '%s_view_columns_present' % cls.obj_name_sub
        cols_present = utils.stg_get_setting(cols_present_prop, [])
        char = utils.object_commands.get(cls.obj_name_sub, {}).get('char', '')

        for col in cols:
            if col['prop'] not in cols_present:
                continue
            value = utils.stg_get_property_value(obj, col)

            if value is not None:
                cols_data.append('%s: %s%s' % (col['colname'], char if col['prop'] in ['id', 'iid'] else '', value))
        cols_data[1] = '**%s**' % cols_data[1]
        cols_data_print = ' | '.join(cols_data)
        return '* %s\n' % cols_data_print

    def run(self, edit, obj_id=None, project_id=None):
        self.obj_id = obj_id if obj_id else self.view.settings().get('object_id')
        self.project_id = project_id if project_id else self.view.settings().get('project_id')

        if not self.obj_id:
            raise Exception('%(name)s id is not defined. %(name)s can not be opened.' % {'name': self.obj_name})

        if not self.project_id:
            raise Exception('Project is not defined. %s can not be opened.' % self.obj_name)

        try:
            self.st_gitlab_view(edit)
        except Exception as e:
            traceback.print_exc()
            sublime.status_message('%s #%s cannot be opened: %s' % (self.obj_name, obj_id, e))

    def get_shortcuts(self, view):
        StShortcutsMenu(view, shortcuts=self.shortcuts, cols=self.cols)

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
        header += line_format.format('**Project**', self.gitlab.project().name)
        header += '\n'
        for col in cols:
            value = utils.stg_get_property_value(obj, col)

            if value is not None:
                line = line_format.format('**%s**' % col['colname'], value)
                cols_data.append(line)

        cols_data_print = '\n'.join(cols_data)
        header += cols_data_print
        header += '\n'
        header += BLOCK_LINE
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
            note_is_system = note_attrs.get('system', False)

            if not utils.stg_get_setting('show_system_notes') and note_is_system:
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

    def screen_name(self):
        return 'st_gitlab_%s' % self.obj_name_sub

    def set_view_settings(self, view):
        screen = self.screen_name()
        view.settings().set('object_id', self.obj_id)
        view.settings().set('project_id', self.project_id)
        view.settings().set('screen', screen)
        view.settings().set('object_name', self.obj_name_sub)
        view.settings().set('st_gitlab_unselectable', True)
        view.set_name('%s #%s' % (self.obj_name, self.obj_id))

    def st_gitlab_view(self, edit):
        obj_current_id = self.view.settings().get('object_id')

        if obj_current_id == self.obj_id:
            r = self.view
            r.set_read_only(False)
            r.erase(edit, sublime.Region(0, self.view.size()))
        else:
            r = sublime.active_window().new_file()
            r.set_scratch(True)
            syntax_file = utils.stg_get_setting('syntax_file')
            r.set_syntax_file(syntax_file)

        # self.gitlab = utils.gl.get()  # creates with current view => r
        self.gitlab = utils.gl.get()  # creates with current view => r
        self.set_view_settings(r)
        # obj = self.gitlab.object_by_screen(r.settings().get('screen'))
        obj = self.gitlab.object_by_view()
        header_print = self.get_header(obj)
        # shortcuts_print = self.get_shortcuts()
        self.get_shortcuts(r)
        description_print = self.get_description(obj)
        object_custom_print = self.get_object_custom(obj)
        notes_print = self.get_notes(obj)

        content = ''
        # content += shortcuts_print
        content += '\n'
        content += header_print
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
        sublime.set_timeout_async(utils.stg_show_images(r), 0)
        r.run_command('st_gitlab_view_show_labels')
        r.set_read_only(True)


class StGitlabIssueFetcherCommand(StGitlabFetcherCommand):

    shortcuts = OrderedDict([
        ('refresh', ['F5', 'refresh']),
        ('title', ['F2', 'change title']),
        ('branch', ['F7', 'create branch']),
        ('descr', ['d', 'change description']),
        ('addnote', ['c', 'add note']),
        ('chnote', ['Alt+c', 'change note']),
        ('state', ['s', 'set state']),
        ('setmile', ['m', 'set milestone']),
        ('labeladd', ['l', 'label add']),
        ('labeldel', ['Alt+l', 'label remove']),
        ('assign', ['a', 'assing to']),
        ('browser', ['g', 'open in browser']),
        ('move', ['p', 'move to project']),
        ('togglemode', ['Alt+u', 'toggle select mode']),
        ('togglenotes', ['Alt+r', 'toggle system notes']),
        ('openlink', ['w', 'open link']),
        ('change', ['Enter', 'change']),
        ('delete', ['Delete', 'delete']),
        ('toggletask', ['x', 'toggle task'])
    ])

    cols = [
        ['refresh', 'title', 'descr', 'state'],
        ['addnote', 'labeladd', 'setmile', 'assign'],
        ['chnote', 'labeldel', 'togglemode', 'togglenotes'],
        ['browser', 'openlink', 'move', 'branch'],
        ['toggletask', 'delete', 'change']
    ]

    obj_name = 'Issue'
    obj_name_sub = 'issue'

    def get_object_custom(self, obj):
        branches = self.gitlab.branches()
        content = ''
        if branches:
            content += '## Related branches\n'
            i = 1
            for br in branches:
                if br.name.startswith(str(obj.iid)):
                    content += '%s. **%s**: %s by %s\n' % (i, br.name, br.commit.get('title'), br.commit.get('author_name'))
        return content


class StGitlabMergeFetcherCommand(StGitlabFetcherCommand):

    shortcuts = OrderedDict([
        ('refresh', ['F5', 'refresh']),
        ('title', ['F2', 'change title']),
        ('descr', ['d', 'change description']),
        ('addnote', ['c', 'add note']),
        ('chnote', ['Alt+c', 'change note']),
        ('state', ['s', 'set state']),
        ('setmile', ['m', 'set milestone']),
        ('labeladd', ['l', 'label add']),
        ('labeldel', ['Alt+l', 'label remove']),
        ('assign', ['a', 'assing to']),
        ('browser', ['g', 'open in browser']),
        ('wip', ['i', 'toggle wip']),
        ('togglemode', ['Alt+u', 'toggle select mode']),
        ('togglenotes', ['Alt+r', 'toggle system notes']),
        ('openlink', ['w', 'open link']),
        ('change', ['Enter', 'change']),
        ('accept', ['p', 'accept']),
        ('toggletask', ['x', 'toggle task'])
    ])

    cols = [
        ['refresh', 'title', 'descr', 'state'],
        ['addnote', 'labeladd', 'setmile', 'assign'],
        ['chnote', 'labeldel', 'togglemode', 'togglenotes'],
        ['browser', 'openlink', 'wip', 'accept'],
        ['toggletask', 'change']
    ]

    obj_name = 'Merge-request'
    obj_name_sub = 'merge'

    def get_object_custom(self, obj):
        issues = obj.closes_issues()
        commits = obj.commits()
        content = ''
        if issues or commits:
            content += '## Data\n'
            content += BLOCK_LINE
            if issues:
                content += '### Closes issues\n'
                for issue in issues:
                    issue_content = StGitlabIssueFetcherCommand.present(issue)
                    content += issue_content
                    content += '\n'
            if commits:
                content += '### Commits (%s)\n' % len(commits)
                for commit in commits:
                    content += '- By %s: [%s](%s)\n' % (
                        commit.committer_name,
                        commit.title,
                        self.get_commit_url(commit)
                    )
            content += '\n'
        branch_name = obj.attributes.get('source_branch')
        pipelines = self.gitlab.pipelines(ref=branch_name)
        if pipelines:
            content += '## Pipeline\n'
            pipeline_id = max([p.id for p in pipelines])
            pipeline = self.gitlab.pipeline(oid=pipeline_id)
            pipeline_content = StGitlabPipelineFetcherCommand.present(pipeline)
            content += pipeline_content
        return content

    def get_commit_url(self, commit):
        return '%(url)s/%(project)s/commit/%(pid)s' % {
            'url': utils.stg_get_setting('gitlab_url'),
            'project': self.gitlab.project(oid=self.project_id).attributes.get('path_with_namespace'),
            'pid': commit.id
        }


class StGitlabPipelineFetcherCommand(StGitlabFetcherCommand):

    shortcuts = OrderedDict([
        ('refresh', ['F5', 'refresh']),
        ('retry', ['b', 'retry']),
        ('cancel', ['c', 'cancel']),
        ('browser', ['g', 'open in browser']),
        ('togglemode', ['Alt+u', 'toggle select mode'])
    ])

    cols = [
        ['refresh'], ['retry'], ['cancel'], ['browser'], ['togglemode']
    ]

    obj_name = 'Pipeline'
    obj_name_sub = 'pipeline'

    def get_title(self, obj):
        return obj.attributes.get('ref', '')

    def get_description(self, obj):
        return ''

    def get_notes(self, obj):
        return ''

    def get_object_custom(self, obj):
        jobs = self.gitlab.jobs()
        if not jobs:
            return
        pipeline_jobs = [j for j in jobs if j.attributes.get('pipeline') == obj.id]
        content = ''
        if pipeline_jobs:
            content += '## Jobs\n'
            content += BLOCK_LINE
            for job in pipeline_jobs:
                content += '* %s **%s**' % (job.id, job.name)
                content += '\n'
        return content


class StGitlabSnippetFetcherCommand(StGitlabFetcherCommand):

    shortcuts = OrderedDict([
        ('refresh', ['F5', 'refresh']),
        ('title', ['F2', 'change title']),
        ('descr', ['d', 'change description']),
        ('addnote', ['c', 'add note']),
        ('chnote', ['Alt+c', 'change note']),
        ('browser', ['g', 'open in browser']),
        ('togglemode', ['Alt+u', 'toggle select mode']),
        ('togglenotes', ['Alt+r', 'toggle system notes']),
        ('openlink', ['w', 'open link']),
        ('change', ['Enter', 'change']),
        ('delete', ['Delete', 'delete']),
        ('toggletask', ['x', 'toggle task'])
    ])

    cols = [
        ['refresh', 'title', 'descr'],
        ['addnote'],
        ['chnote', 'togglemode', 'togglenotes'],
        ['browser', 'openlink'],
        ['toggletask', 'delete', 'change']
    ]

    obj_name = 'Snippet'
    obj_name_sub = 'snippet'

    def get_object_custom(self, obj):
        raw = obj.content()
        print(raw)
        if not raw:
            return
        from io import BytesIO
        fp = BytesIO(raw)
        content = '## %s\n' % obj.file_name
        content += BLOCK_LINE
        content += fp.read().decode('utf-8').replace('\r', '')
        content += '\n'
        return content

