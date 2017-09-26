#!/usr/bin/env python\n
# -*- coding: utf-8 -*-
import re
import base64
import requests
import sublime
from datetime import datetime
from .stg_gitlab import StGitlab

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

gl = StGitlab()


def stg_get_setting(key, default_value=None):
    settings = sublime.load_settings('StGitlab.sublime-settings')
    return settings.get(key, default_value)


def stg_set_setting(key, value):
    settings = sublime.load_settings('StGitlab.sublime-settings')
    settings.set(key, value)
    sublime.save_settings('Mediawiker.sublime-settings')


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

    gitlab = gl.get()
    labels = gitlab.labels(project_id=project_id, all=True)
    msg = re.sub(label_pattern, get_label, msg)
    return msg


def stg_get_image(url):
    response = requests.get(url)
    img_base64 = "data:" + response.headers['Content-Type'] + ";" + "base64," + str(base64.b64encode(response.content).decode("utf-8"))
    return img_base64


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
        view.add_phantom(
            'image',
            sublime.Region(image_r.b + 1, image_r.b + 2),
            '<img src="%s"><br><br>' % (stg_get_image(img_url)),
            sublime.LAYOUT_BLOCK
        )
