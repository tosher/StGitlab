#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

import sublime
import sublime_plugin
from .stg_gitlab import StGitlab
from . import stg_utils as utils


class StGitlabViewShowLabelsCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        self.view.erase_phantoms('label')
        gitlab = StGitlab()
        lbs = gitlab.labels(all=True)

        lbl_chr = utils.stg_get_setting('label_char')
        lbl_pattern = r'\%(lchr)s[^\%(lchr)s]+\%(lchr)s' % {'lchr': lbl_chr}
        labels = self.view.find_all(lbl_pattern)
        for label_r in labels:
            lbl_text = self.view.substr(label_r)[1:-1]
            lbl_color = '#D84315'
            try:
                for lab in lbs:
                    if lab.attributes.get('name', None) == lbl_text:
                        lbl_color = lab.attributes.get('color', '#D84315')
                        break
            except Exception as e:
                print('Label exception: %s' % e)

            self.view.add_phantom(
                'label',
                sublime.Region(label_r.a, label_r.a),
                '<span style="background-color:%s;border-radius:0.2rem;font-size:1rem;margin:0;">&nbsp;%s&nbsp;</span>' % (lbl_color, lbl_text),
                sublime.LAYOUT_INLINE
            )

        r_offset = 0
        for label_r in labels:
            r = sublime.Region(label_r.a - r_offset, label_r.b - r_offset)
            self.view.erase(edit, r)
            r_offset += r.size()
