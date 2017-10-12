#!/usr/bin/env python\n
# -*- coding: utf-8 -*-
import re
import base64
import requests
import sublime
from datetime import datetime, timedelta
from .stg_gitlab import StGitlab
from ..libs import dimensions


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

object_commands = {
    'issue': {
        'char': '#',
        'screen_view': 'st_gitlab_issue',
        'screen_list': 'st_gitlab_issues',
        'screen_board': 'st_gitlab_issues_board',
        'view': 'st_gitlab_issue',
        'list': 'st_gitlab_project_issues_list',
        'fetch': 'st_gitlab_issue_fetcher'
    },
    'merge': {
        'char': '!',
        'screen_view': 'st_gitlab_merge',
        'screen_list': 'st_gitlab_merges',
        'screen_board': None,
        'view': 'st_gitlab_merge',
        'list': 'st_gitlab_project_merges_list',
        'fetch': 'st_gitlab_merge_fetcher'
    },
    'pipeline': {
        'screen_view': 'st_gitlab_pipeline',
        'screen_list': 'st_gitlab_pipelines',
        'screen_board': None,
        'view': 'st_gitlab_pipeline',
        'list': 'st_gitlab_project_pipelines_list',
        'fetch': 'st_gitlab_pipeline_fetcher'
    },
    'branch': {
        'screen_view': None,
        'screen_list': 'st_gitlab_branches',
        'screen_board': None,
        'view': None,
        'list': 'st_gitlab_project_branches_list',
        'fetch': None
    },
    'snippet': {
        'screen_view': 'st_gitlab_snippet',
        'screen_list': 'st_gitlab_snippets',
        'screen_board': None,
        'view': 'st_gitlab_snippet',
        'list': 'st_gitlab_project_snippets_list',
        'fetch': 'st_gitlab_snippet_fetcher'
    }
}

gl = StGitlab()


def stg_get_setting(key, default_value=None):
    settings = sublime.load_settings('StGitlab.sublime-settings')
    return settings.get(key, default_value)


def stg_set_setting(key, value):
    settings = sublime.load_settings('StGitlab.sublime-settings')
    settings.set(key, value)
    sublime.save_settings('Mediawiker.sublime-settings')


# def stg_validate_screen(screen_type):
#     if isinstance(screen_type, list):
#         is_valid = sublime.active_window().active_view().settings().get('screen', None) in screen_type
#         object_name = ', '.join([screen.split('_')[-1] for screen in screen_type])
#     else:
#         is_valid = screen_type == sublime.active_window().active_view().settings().get('screen', None)
#         object_name = screen_type.split('_')[-1]

#     if not is_valid:
#         sublime.message_dialog('This command is provided for the %s screen!' % object_name)


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


def stg_get_seconds(seconds):
    try:
        return str(timedelta(seconds=int(seconds)))
    except Exception as e:
        print('Duration convert exception for value "%s": %s' % (seconds, e))
        return seconds


def stg_cut(val, maxlen):
    if maxlen:
        if len(val) > maxlen:
            return '%s..' % val[:maxlen - 2].strip()
    return val


def stg_get_property_value(obj, prop):
    val = ''
    label_char = stg_get_setting('label_char')
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
        elif prop_type == 'seconds':
            val = stg_get_seconds(attrs.get(prop['prop'], ''))
        elif prop_type == 'bool':
            val = str(attrs.get(prop['prop'], ''))
        elif prop.get('attr', None):
            val_obj = attrs.get(prop['prop'], '')
            if val_obj:
                if isinstance(val_obj, str):
                    val = val_obj
                else:
                    val = val_obj.get(prop['attr'], '')
        else:
            val = attrs.get(prop['prop'], '')
        return stg_cut(val, prop.get('maxlen', None))
    except Exception as e:
        print('Exception while get %s value: %s' % (prop, e))
        return attrs.get(prop['prop'], '')


def stg_msg_labels(msg, project_id):
    def get_label(matched):
        label_id = matched.group(2)
        labs = [lab.name for lab in labels if lab.id == int(label_id)]
        if labs:
            return '%(lchr)s%(lname)s%(lchr)s' % {'lchr': lbl_chr, 'lname': labs[0]}
        return '~%s' % label_id

    lbl_chr = stg_get_setting('label_char')
    label_pattern = r'(^|\s)\~(\d+)'
    m = re.search(label_pattern, msg)
    if not m or not m.group(2):
        return msg

    gitlab = gl.get()
    labels = gitlab.labels(project_id=project_id, all=True)
    msg = re.sub(label_pattern, get_label, msg)
    return msg


def stg_get_image(url):
    max_width = stg_get_setting('image_max_width')
    response = requests.get(url)
    dims = dimensions.get_dimensions_from_stream(response.content)
    w, h = stg_image_scale(dims[0], dims[1], max_width)
    img_base64 = "data:" + response.headers['Content-Type'] + ";" + "base64," + str(base64.b64encode(response.content).decode("utf-8"))
    return img_base64, w, h


def stg_show_images(view):
    view.erase_phantoms('image')
    img_pattern = r'!\[(.*?)(\])\((.*?)\)'
    images = view.find_all(img_pattern)
    for image_r in images:
        img_text = view.substr(image_r)
        img_url = img_text.split('(')[1][:-1]
        if not img_url.startswith('http'):
            gitlab = gl.get()
            project = gitlab.project()
            img_url = '/'.join([project.web_url.rstrip('/'), img_url.lstrip('/')])
        img_data, w, h = stg_get_image(img_url)
        view.add_phantom(
            'image',
            sublime.Region(image_r.b + 1, image_r.b + 2),
            '<img src="%s" width="%s" height="%s"><br><br>' % (img_data, w, h),
            sublime.LAYOUT_BLOCK
        )


def stg_image_scale(width, height, max_width):
    width = float(width)
    height = float(height)
    scaled = False
    if not max_width:
        return width, height

    if width > max_width:
        koeff = width / max_width
        width = max_width
        height = height / koeff
        scaled = True

    if scaled:
        return int(width), int(height)
    return width, height
