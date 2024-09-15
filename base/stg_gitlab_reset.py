#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

import sublime_plugin  # type:ignore

from . import utils


class StGitlabResetCommand(sublime_plugin.ApplicationCommand):
    def run(self) -> None:
        gitlab = utils.gl.get()
        gitlab.reset()
