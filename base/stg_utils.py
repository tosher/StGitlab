#!/usr/bin/env python\n
# -*- coding: utf-8 -*-
import sys
import os
import re
import base64
import requests
import sublime
from datetime import datetime
from .stg_gitlab import StGitlab
sys.path.append(os.path.join(os.path.dirname(__file__), "../libs"))
from terminaltables.other_tables import WindowsTable as SingleTable


filter_types = {
    'Author': 'author_id',
    'Assignee': 'assignee_id',
    'Labels': 'labels',
    'Milestone': 'milestone',
    'State': 'state',
    'Search': 'search',
    'Page number': 'page',
    'Reset filters': None
}


def stg_get_setting(key, default_value=None):
    settings = sublime.load_settings('StGitlab.sublime-settings')
    return settings.get(key, default_value)


def stg_validate_screen(screen_type):
    if isinstance(screen_type, list):
        is_valid = sublime.active_window().active_view().settings().get('screen', None) in screen_type
        object_name = ', '.join([screen.split('_')[-1] for screen in screen_type])
    else:
        is_valid = screen_type == sublime.active_window().active_view().settings().get('screen', None)
        object_name = screen_type.split('_')[-1]

    if not is_valid:
        sublime.message_dialog('This command is provided for the %s screen!' % object_name)


def stg_get_datetime(datetime_str):
    if not datetime_str:
        return datetime_str

    dt_format_in = stg_get_setting('datetime_format')
    dt_format_sys_1 = '%Y-%m-%dT%H:%M:%S.%fZ'
    dt_format_sys_2 = '%Y-%m-%dT%H:%M:%S.%f%z'
    dt_format_out = stg_get_setting('datetime_format_show')

    dt_str_cnv = str(datetime_str)
    if '%z' in dt_format_in:
        # datetime_str = '2017-09-18T16:53:33.197+03:00'
        # dt_format_in = '%Y-%m-%dT%H:%M:%S.%f%z'
        # remove unsupported : in ..+03:00
        dt_str_cnv = ''.join(datetime_str.rsplit(':', 1))

    # TODO: research time formats in gitlab
    try:
        datetime_obj = datetime.strptime(dt_str_cnv, dt_format_in)
        return datetime_obj.strftime(dt_format_out)
    except ValueError:
        try:
            datetime_obj = datetime.strptime(datetime_str, dt_format_sys_1)
            return datetime_obj.strftime(dt_format_out)
        except ValueError as e:
            try:
                dt_str_cnv = ''.join(datetime_str.rsplit(':', 1))
                datetime_obj = datetime.strptime(dt_str_cnv, dt_format_sys_2)
                return datetime_obj.strftime(dt_format_out)
            except ValueError as e:
                print('Error converting datetime string "%s": %s (1)' % (dt_str_cnv, e))
                return datetime_str.replace('T', ' ').replace('Z', '')
        except Exception as e:
            print('Error converting datetime string "%s": %s (2)' % (datetime_str, e))
            return datetime_str.replace('T', ' ').replace('Z', '')
    except Exception as e:
        print('Error converting datetime string "%s": %s (3)' % (dt_str_cnv, e))
        return datetime_str.replace('T', ' ').replace('Z', '')


def stg_get_property_value(obj, prop):
    def cut(val, maxlen):
        if maxlen:
            if len(val) > maxlen:
                return '%s..' % val[:maxlen - 2].strip()
        return val

    val = ''
    label_char = '•'
    prop_type = prop.get('type', 'string')
    attrs = obj.attributes
    try:
        if prop_type == 'list':
            if prop['prop'] == 'labels':
                val = ' '.join(['%s%s%s' % (label_char, lab, label_char) for lab in attrs.get(prop['prop'], '')])
            else:
                val = ', '.join(attrs.get(prop['prop'], ''))
        elif prop_type == 'datetime':
            val = stg_get_datetime(attrs.get(prop['prop'], ''))
        elif prop.get('attr', None):
            val_obj = attrs.get(prop['prop'], '')
            if val_obj:
                if isinstance(val_obj, str):
                    val = val_obj
                else:
                    val = val_obj.get(prop['attr'], '')
        else:
            val = attrs.get(prop['prop'], '')
        return cut(val, prop.get('maxlen', None))
    except Exception as e:
        print('Exception while get %s value: %s' % (prop, e))
        return attrs.get(prop['prop'], '')


def stg_msg_labels(msg, project_id):
    def get_label(matched):
        label_id = matched.group(1)
        labs = [lab.name for lab in labels if lab.id == int(label_id)]
        if labs:
            return '%(lchr)s%(lname)s%(lchr)s' % {'lchr': lbl_chr, 'lname': labs[0]}
        return '~%s' % label_id

    lbl_chr = stg_get_setting('label_char')
    label_pattern = r'\~(\d+)'
    m = re.search(label_pattern, msg)
    if not m or not m.group(1):
        return msg

    gitlab = StGitlab.connect()
    project = gitlab.projects.get(project_id)
    labels = project.labels.list(all=True)
    msg = re.sub(label_pattern, get_label, msg)
    return msg


def stg_get_image(url):
    response = requests.get(url)
    img_base64 = "data:" + response.headers['Content-Type'] + ";" + "base64," + str(base64.b64encode(response.content).decode("utf-8"))
    return img_base64


# set_timeout_async(process_red_links(view, page), 0)
def stg_show_images(view):
    img_pattern = r'!\[(.*?)(\])\((.*?)\)'
    images = view.find_all(img_pattern)
    for image_r in images:
        img_text = view.substr(image_r)
        img_url = img_text.split('(')[1][:-1]
        if not img_url.startswith('http'):
            project_id = view.settings().get('project_id', None)
            gitlab = StGitlab.connect()
            project = gitlab.projects.get(project_id)
            img_url = '/'.join([project.web_url.rstrip('/'), img_url.lstrip('/')])
        view.add_phantom(
            'image',
            sublime.Region(image_r.b + 1, image_r.b + 2),
            '<img src="%s"><br><br>' % (stg_get_image(img_url)),
            sublime.LAYOUT_BLOCK
        )


# ### Issues list ###
def stg_show_issues(title, **kwargs):
    gitlab = StGitlab.connect()
    # shortcuts = [
    #     '[Enter](open)',
    #     '[r](refresh)',
    #     '[d](delete)',
    #     '[f](filter)',
    #     '[Shift + <-](prev. page)',
    #     '[Shift + ->](next page)'
    # ]
    html = '''
    <html>
        <style>
            tt.kbd {
                color: #C5C2A2;
                background-color: #555555;
                font-size: 1rem;
                border-radius: 0.6rem;
                padding: 0.2rem;
                padding-left: 0.4rem;
                padding-right: 0.4rem;
            }

            span.keyname {
                color: #c0c0c0;
                font-size: 1rem;
                padding: 0.2rem;
                padding-left: 0.3rem;
                padding-right: 0.4rem;
            }
        </style>
        <body id="gitlab" style="padding:0;margin:0;">
            <tt class="kbd">Enter</tt><span class="keyname">open</span>
            <tt class="kbd">r</tt><span class="keyname">refresh</span>
            <tt class="kbd">Delete</tt><span class="keyname">delete</span>
            <tt class="kbd">f</tt><span class="keyname">filter</span>
            <tt class="kbd">Shift + →</tt><span class="keyname">prev. page</span>
            <tt class="kbd">Shift + ←</tt><span class="keyname">next page</span>
        </body>
    </html>
    '''

    sublime.active_window().active_view().add_phantom(
        'label',
        sublime.Region(0, 0),
        html,
        sublime.LAYOUT_INLINE
    )

    # content_header = '%s\n\n' % ' '.join(shortcuts)
    content_header = '\n\n'
    if title:
        content_header += '## %s\n' % title

    project = gitlab.projects.get(kwargs.get('project_id'))
    issues = project.issues.list(**kwargs)
    content_header += '\t**Total**: %s\n' % len(issues)
    content_header += '\t**Page number**: %s (%s issues per page)\n' % (kwargs.get('page', 1), kwargs.get('per_page'))
    content_header += '\t**Filters**:\n'
    for name in filter_types.values():
        if name in kwargs:
            if name == 'labels':
                labels = ', '.join(['^%s^' % label for label in kwargs.get(name)])
                content_header += '\t\t**%s**: %s\n' % (name, labels)
            else:
                content_header += '\t\t**%s**: %s\n' % (name, kwargs.get(name))
    content_header += '\n'

    cols = stg_get_setting('issue_list_columns', {})

    tbl_header = [col['colname'] for col in cols]

    table_data = [
        tbl_header
    ]

    for issue in issues:
        iss = []
        for col in cols:
            iss.append(stg_get_property_value(issue, col))
        table_data.append(iss)

    issues_table = SingleTable(table_data)
    return content_header + issues_table.table


# ### Merge-requests list ###

def stg_show_merges(title, **kwargs):
    gitlab = StGitlab.connect()

    shortcuts = [
        '[Enter](open)',
        '[r](refresh)',
        '[f](filter)',
        '[Shift + <-](prev. page)',
        '[Shift + ->](next page)'
    ]

    content_header = '%s\n\n' % ' '.join(shortcuts)
    if title:
        content_header += '## %s\n' % title

    project = gitlab.projects.get(kwargs.get('project_id'))
    mrs = project.mergerequests.list(**kwargs)
    content_header += '\t**Total**: %s\n' % len(mrs)
    content_header += '\t**Page number**: %s (%s merge-requests per page)\n' % (kwargs.get('page', 1), kwargs.get('per_page'))
    content_header += '\t**Filters**:\n'
    for name in filter_types.values():
        if name in kwargs:
            if name == 'labels':
                labels = ', '.join(['^%s^' % label for label in kwargs.get(name)])
                content_header += '\t\t**%s**: %s\n' % (name, labels)
            else:
                content_header += '\t\t**%s**: %s\n' % (name, kwargs.get(name))
    content_header += '\n'

    cols = stg_get_setting('merge_requests_list_columns', {})

    tbl_header = [col['colname'] for col in cols]

    table_data = [
        tbl_header
    ]
    for mr in mrs:
        m = []
        for col in cols:
            m.append(stg_get_property_value(mr, col))
        table_data.append(m)

    mrs_table = SingleTable(table_data)
    return content_header + mrs_table.table


# ### Pipelines list ###
def stg_show_pipelines(title, **kwargs):
    gitlab = StGitlab.connect()

    shortcuts = [
        '[Enter](open)',
        '[r](refresh)',
        '[b](retry)',
        '[c](cancel)',
        '[f](filter)',
        '[Shift + <-](prev. page)',
        '[Shift + ->](next page)'
    ]

    content_header = '%s\n\n' % ' '.join(shortcuts)
    if title:
        content_header += '## %s\n' % title

    project = gitlab.projects.get(kwargs.get('project_id'))
    pls = project.pipelines.list(**kwargs)
    content_header += '\t**Total**: %s\n' % len(pls)
    content_header += '\t**Page number**: %s (%s pipelines per page)\n' % (kwargs.get('page', 1), kwargs.get('per_page'))
    content_header += '\t**Filters**:\n'
    for name in filter_types.values():
        if name in kwargs:
            if name == 'labels':
                labels = ', '.join(['^%s^' % label for label in kwargs.get(name)])
                content_header += '\t\t**%s**: %s\n' % (name, labels)
            else:
                content_header += '\t\t**%s**: %s\n' % (name, kwargs.get(name))
    content_header += '\n'

    cols = stg_get_setting('pipelines_list_columns', {})

    tbl_header = [col['colname'] for col in cols]

    table_data = [
        tbl_header
    ]
    for pl in pls:
        print(dir(pl))
        p = []
        for col in cols:
            p.append(stg_get_property_value(pl, col))
        table_data.append(p)

    mrs_table = SingleTable(table_data)
    return content_header + mrs_table.table
