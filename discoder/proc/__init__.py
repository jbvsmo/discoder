# coding: utf-8
""" Copyright (c) 2013 João Bernardo Vianna Oliveira

    This file is part of Discoder.

    Discoder is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    Discoder is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with Discoder.  If not, see <http://www.gnu.org/licenses/>.
"""

import subprocess

__author__ = 'jb'

DEBUG = False
#DEBUG = True

def run_local(cmd, stdout=None, stderr=None, pipe=True):
    """ Run a command in a list of arguments with Popen.
        returns the stdout and stderr outputs.

        :param cmd:
        :param stdout:
        :param stderr:
        :param pipe:
        :return:
    """
    if pipe:
        if stdout is None:
            stdout = subprocess.PIPE
        if stderr is None:
            stderr = subprocess.PIPE
    if DEBUG:
        print(' '.join(cmd))
    return subprocess.Popen(cmd, stdout=stdout, stderr=stderr).communicate()

def run_many(cmds, stdout=None, stderr=None, pipe=True, run=run_local):
    """ Same as run but for more than one command. Might be replaced by
        a distributed approach.
    """
    for c in cmds:
        run(c, stdout, stderr, pipe)
