#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

# import sublime
import sublime_plugin
from . import utils


class StGitlabResetCommand(sublime_plugin.ApplicationCommand):

    def run(self):
        gitlab = utils.gl.get()
        gitlab.reset()


