#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

import math
import itertools
from collections import OrderedDict
import sublime
from . import stg_utils as utils


class StLabel(object):

    EDGE_LIGHT = 150

    # label font-size 0.9 to base
    html_tpl = '''
    <html>
    <style>
    html {
        --bg: %(color)s
    }

    div.label {
        color: %(color_inverted)s;
        background-color:var(--bg);
        font-family: Consolas, Menlo, Tahoma, Courier, monospace;
        font-size: 0.9rem;
        padding-top: 2px;
        padding-left: 6px;
        padding-right: 6px;
        padding-bottom: 0;
        border-width: 1px;
        border-radius: 3px;
        border-style: solid;
        border-color: color(white blend(var(--bg) 40%%));
        margin:0;
        margin-left:4px;
    }

    div.in_note {
        font-size: 0.7rem;
        padding-top: 0px;
        padding-bottom: 1px;
    }

    div.in_note_grayed {
        font-size: 0.7rem;
        background-color: color(var(--bg) blend(gray 30%%));
        border-color: color(var(--bg) blend(gray 30%%));
        padding-top: 0px;
        padding-bottom: 1px;
    }

    </style>
    <body>
        <div class="%(label_class)s">%(text)s</div>
    </body>
    </html>'''

    def __init__(self, text, color, grayed=False):
        self.text = text
        self.grayed = grayed
        self.color = color

    def get(self):
        is_grayout_labels_in_notes = utils.stg_get_setting('grayed_out_labels_in_notes')
        label_class = 'label' if not self.grayed else 'label in_note_grayed' if is_grayout_labels_in_notes else 'label in_note'
        return self.html_tpl % {
            'text': self.text,
            'color': self.color,
            'color_inverted': self.blackwhite(self.color),
            'label_class': label_class
        }

    def blackwhite(self, hexcolor):
        hexcolor = hexcolor.lstrip('#')
        rgb = (int(hexcolor[0:2], 16), int(hexcolor[2:4], 16), int(hexcolor[4:6], 16))
        pairs = list(itertools.combinations(rgb, 2))
        for pair in pairs:
            if all([x < self.EDGE_LIGHT for x in pair]):
                return '#fff'
        return '#000'

    def complimentary_color(self, hexcolor):
        # if hexcolor[0] == '#':
        #     hexcolor = hexcolor[1:]
        # rgb = (hexcolor[0:2], hexcolor[2:4], hexcolor[4:6])
        # comp = ['%02X' % (255 - int(a, 16)) for a in rgb]
        # return '#' + ''.join(comp)
        return "#%06X" % (int(hexcolor.lstrip('#'), 16) ^ 0xffffff)


class StShortcutsMenu(object):
    # keys font size is fixed
    html_tpl = '''
    <html>
        <style>
            div.keyline {
                margin-bottom: 0.6rem;
            }

            span.kbd {
                color: #444446;
                background-color: #F3F3F4;
                font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, Courier, monospace;
                font-size: 8pt;
                padding: 2px;
                padding-left: 6px;
                padding-right: 6px;
                margin-right: 40px;
                border: 2px solid #DCDCDC;
                border-radius: 4px;
            }

            span.kbd2 {
                padding-left: 3px;
                padding-right: 3px;
            }

            span.kbdplus {
                color: #DCDCDC;
                font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, Courier, monospace;
                font-size: 8pt;
                border-radius: 2px;
                padding: 2px;
                padding-left: 4px;
                padding-right: 4px;
            }

            span.keyname {
                color: #c0c0c0;
                font-size: 8pt;
                font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, Courier, monospace;
                padding: 0.2rem;
                padding-left: 0.5rem;
                padding-right: 0;
            }

            li {
                margin-left: -40px;
                padding: 0.2rem;
            }
        </style>
        <body id="gitlab" style="padding:0;margin:0;padding-top:-1rem;">
        %(shortcuts)s
        </body>
    </html>
    '''

    html_col_tpl = '<div style="display: block;padding:0;margin:0;"><ul>%(list)s</ul></div>'
    html_shortcut_tpl = '<li>%(keyname)s<span class="keyname">%(cmdname)s</span></li>'
    html_key_tpl = '<span class="%(kbdclass)s">%(key)s</span>'
    html_key_plus = '<span class="kbdplus">+</span>'

    def __init__(self, view, shortcuts, cols=5, by_cols=None):
        if not shortcuts:
            return
        if isinstance(cols, int):
            cols_cnt = cols
            cols = [[] for _ in range(cols_cnt)]
            for idx, k in enumerate(shortcuts.keys()):
                cols[self.key_col(cols_cnt, idx)].append(k)
        elif cols is None:
            cols = [[k for k in shortcuts.keys()]]

        cols_html = []
        for col in cols:
            keys = []
            for k in col:
                line = self.html_shortcut_tpl % {'keyname': self.show_key(shortcuts[k][0]), 'cmdname': shortcuts[k][1]}
                keys.append(line)
            col_html = self.html_col_tpl % {'list': ''.join(keys)}
            cols_html.append(col_html)

        view.erase_phantoms('shortcuts')
        for idx, block in enumerate(cols_html):
            shortcuts_menu_html = self.html_tpl % {'shortcuts': block}
            view.add_phantom(
                'shortcuts',
                sublime.Region(0, 0),
                shortcuts_menu_html,
                sublime.LAYOUT_INLINE
            )

    def key_col(self, cols, keyidx):
        return keyidx - math.floor(keyidx / cols) * cols

    def key_class(self, key):
        if len(key) == 2:
            return 'kbd kbd2'
        return 'kbd'

    def show_key(self, keyname):
        keys = keyname.split('+')
        # return '<span style="padding:1px;">+</span>'.join(['<span style="color:#FBB788;">%s</span>' % k for k in keys])
        return self.html_key_plus.join([self.html_key_tpl % {'kbdclass': self.key_class(k), 'key': k} for k in keys])


class StNotesIcons(object):

    # https://gitlab.com/gitlab-org/gitlab-ce/issues/33503
    icon_markers = OrderedDict([
        ('label', 'lable.png'),
        ('marked', 'pencil.png'),
        ('milestone', 'clock.png'),
        ('task completed', 'task-done.png'),
        ('task incomplete', 'task-undone.png'),
        ('mention merge', 'systemnote-mentioned-mr.png'),
        ('enabled merge', 'icon-merge-request.png'),
        ('approved', 'approval.png'),
        ('merged', 'icon-merge-request.png'),
        ('mention issue', 'icon-mention.png'),
        ('assigned to', 'assignee.png'),
        ('removed assigne', 'unassignee.png'),
        ('changed', 'pencil.png'),
        ('create branch', 'branch.png'),
        ('move project', 'arrow-right.png'),
        ('commit', 'systemnote-commit.png'),
        ('close', 'systemnote-status-closed.png'),
        ('reopen', 'systemnote-status-open.png'),
        ('comment', 'comment.png'),
        ('duplicate', 'duplicate.png'),
        ('confidential', 'eye-slash.png'),
        ('visible', 'eye.png')
    ])

    def __init__(self, view):
        self.view = view
        self.build()

    def build(self):
        self.view.erase_phantoms('note_icon')
        pattern = r'^> \d+:(.*?)$'
        notes = self.view.find_all(pattern)
        for note in notes:
            text = ' '.join(self.view.substr(note).split()[2:])
            self.show(note.a, text)

    def get_icon(self, text):
        for marker in self.icon_markers.keys():
            marker_tokens = marker.split()
            if all([m in text.lower() for m in marker_tokens]):
                return self.icon_markers[marker]
        return None

    def show(self, point, text):
        icon = self.get_icon(text)
        if not icon:
            return
        self.view.add_phantom(
            'note_icon',
            sublime.Region(point, point),
            '<div style="padding:3px;"><img src="res://Packages/StGitlab/icons/%s" width="%s" height="%s" style="border:0;"></div>' % (icon, 16, 16),
            sublime.LAYOUT_INLINE
        )
