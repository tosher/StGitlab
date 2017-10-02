#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

import math
import itertools
import sublime


class StLabel(object):

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
    </style>
    <body>
        <div class="label">%(text)s</div>
    </body>
    </html>'''

    def __init__(self, text, color):
        self.text = text
        self.color = color

    def get(self):
        return self.html_tpl % {'text': self.text, 'color': self.color, 'color_inverted': self.blackwhite(self.color)}

    def blackwhite(self, hexcolor):
        hexcolor = hexcolor.lstrip('#')
        rgb = (int(hexcolor[0:2], 16), int(hexcolor[2:4], 16), int(hexcolor[4:6], 16))
        pairs = list(itertools.combinations(rgb, 2))
        for pair in pairs:
            if all([x < 127 for x in pair]):
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
