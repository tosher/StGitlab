#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

import sublime
import sublime_plugin
from . import utils
from .stg_html import StLabel


class StGitlabViewShowLabelsCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        labels_points = []
        lbl_chr = utils.get_setting('label_char')
        lbl_pattern = r'\%(lchr)s[^\%(lchr)s]+\%(lchr)s' % {'lchr': lbl_chr}
        labels = self.view.find_all(lbl_pattern)
        r_offset = 0
        for label_r in labels:
            r = sublime.Region(label_r.a - r_offset, label_r.b - r_offset)
            lbl_text = self.view.substr(r)[1:-1]
            line = self.view.substr(self.view.line(r))
            is_in_note = True if line.startswith('> ') else False
            labels_points.append({'label': lbl_text, 'point': label_r.a - r_offset, 'is_in_note': is_in_note})
            self.view.erase(edit, r)
            r_offset += r.size()

        self.view.settings().set('labels_points', labels_points)
        self.__class__.pretty_labels(self.view)

    def pretty_labels(view):
        view.erase_phantoms('label')
        gitlab = utils.gl.get()
        lbs = gitlab.labels(all=True)
        lbl_color_default = '#D84315'
        lbs_colors = {}
        for lab in lbs:
            lbs_colors[lab.attributes.get('name')] = lab.attributes.get('color')

        labels_points = view.settings().get('labels_points')
        if not labels_points:
            return

        for label in labels_points:
            point = label['point']
            lbl_color = lbs_colors.get(label['label'], lbl_color_default)
            grayed = True if label['is_in_note'] else False
            view.add_phantom(
                'label',
                sublime.Region(point, point),
                StLabel(label['label'], lbl_color, grayed=grayed).get(),
                sublime.LAYOUT_INLINE
            )

    def is_visible(self, *args):
        return False
