#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

import sublime


class StShortcutsMenu(object):
    html_tpl = '''
    <html>
        <style>
            tt.kbd {
                color: #C5C2A2;
                background-color: #555555;
                font-size: 1rem;
                border-radius: 0.2rem;
                padding: 0rem;
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
        %(shortcuts)s
        </body>
    </html>
    '''

    html_shortcut_tpl = '<tt class="kbd">%(keyname)s</tt><span class="keyname">%(cmdname)s%(space)s</span>'

    def __init__(self, view, shortcuts, cols=5):
        if not shortcuts:
            return

        maxlen = 0
        if cols:
            shs_simple = ['%(keyname)s %(cmdname)s' % {'keyname': keyname, 'cmdname': shortcuts[keyname]} for keyname in shortcuts.keys()]
            maxlen = len(max(shs_simple, key=len))
        shs = []
        shs.append('<div style="margin:0.1rem;">')
        for idx, keyname in enumerate(shortcuts.keys()):
            space = ''
            if cols:
                space = '&nbsp;' * (maxlen - len('%(keyname)s %(cmdname)s' % {'keyname': keyname, 'cmdname': shortcuts[keyname]}))
            sh = self.html_shortcut_tpl % {'keyname': keyname, 'cmdname': shortcuts[keyname], 'space': space}
            if cols and not idx % cols:
                shs.append('</div>')
                shs.append('<div style="margin:0.2rem;">')
            shs.append(sh)
        shs.append('</div>')
        shortcuts_html = '\n'.join(shs)

        shortcuts_menu_html = self.html_tpl % {'shortcuts': shortcuts_html}
        view.erase_phantoms('shortcuts')
        view.add_phantom(
            'shortcuts',
            sublime.Region(0, 0),
            shortcuts_menu_html,
            sublime.LAYOUT_INLINE
        )
