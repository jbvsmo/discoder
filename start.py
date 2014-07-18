#!/usr/bin/python
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


from __future__ import print_function
import os
import sys

root = os.path.abspath(__file__)
root = os.path.dirname(os.path.dirname(root))

sys.path.insert(0, root)
import optparse
from discoder import distributed
from discoder import run

__author__ = 'jb'


def arg(all=False):
    if all:
        return sys.argv
    return sys.argv.pop(0)
program = arg()

class OptException(Exception): pass
options = ['cluster', 'node', 'probe']


def cmd(name):
    """ Command line parser
    """
    parser = optparse.OptionParser()
    parser.add_option('-l', '--log', dest='log', default='log_{0}.txt'.format(name))
    parser.add_option('-t', '--times', dest='times', default=1, type='int')

    if name == 'cluster':
        parser.add_option('-n', '--nodes', dest='nodes', type='int')
        parser.add_option('--first-node', dest='first_node', type='int', default=0)
        parser.add_option('-i', '--input', dest='input')
        parser.add_option('-f', '--flavor', dest='flavor', default=[], action='append')
        parser.add_option('-p', '--parts', dest='parts', type='int')
        parser.add_option('-w', '--threads', dest='threads', type='int')
        parser.add_option('-r', '--remove', dest='remove', default=False, action="store_true")
        parser.add_option('--fancy-seek', dest='fancy_seek', default=False, action="store_true")
        parser.add_option('-b', '--balance', dest='balance', type='int', default=0)
        parser.add_option('--balance-order', dest='balance_order', default=False, action="store_true")
    elif name == 'node':
        parser.add_option('-d', '--daemon', dest='daemon', default=False, action="store_true")
        parser.add_option('-p', '--port', dest='port', default=distributed.DEFAULT_PORT, type='int')
    elif name == 'probe':
        parser.add_option('-i', '--input', dest='input')
    else:
        print('No such option:', name)
        print('Available options:', *options, sep='\n\t')
        raise OptException

    return parser.parse_args(sys.argv)



if __name__ == '__main__':
    try:
        name = arg()
        opt = cmd(name)
        fn = getattr(run, name)
        fn(opt)
    except OptException:
        pass
