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

from __future__ import print_function, division
import collections
import os
import pprint
import string
import time
import sys

from discoder.conv.transcoder import Transcoder
from discoder.conv.flavor import Flavor
from discoder import distributed
from discoder.distributed import client
from discoder.distributed import server
from discoder.lib import command

__author__ = 'jb'


TimeDescription = collections.namedtuple('TimeDescription', ['time', 'desc'])


class Time(list):

    # noinspection PyTypeChecker
    def add(self, desc=None):
        self.append(TimeDescription(time.time(), desc))
        return self

    def get(self, num):
        if num == 0:
            return 0
        if num == len(self) - 1 or num == -1:
            return self[num].time - self[0].time
        return self[num].time - self[num - 1].time

    def info(self):
        if len(self) < 2:
            return str(self)
        t = '{0.desc}: \t{1}s'
        data = [
            t.format(self[0], self[0].time)
        ]
        for i, x in enumerate(self[1:], 1):
            data.append(t.format(x, self.get(i)))

        return '\n'.join(data)


def letters():
    try:
        return string.ascii_uppercase
    except AttributeError:
        return string.uppercase


def get_nodes():
    """ Get nodes list from file.
    """
    dir = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(dir, 'nodes.txt')) as f:
        data = f.read().splitlines()
    return [distributed.parse_address(i) for i in data]


all_nodes = get_nodes()
run_nodes = all_nodes


def node(opt):
    """ Start client node and wait for requests.
    """
    opt, _ = opt
    if opt.daemon:
        # noinspection PyPackageRequirements
        # noinspection PyUnresolvedReferences
        import daemon
        with daemon.DaemonContext():
            client.start(opt.port)
    else:
        client.start(opt.port)


def cluster(opt):
    opt, _ = opt
    if not opt.input:
        print('[ERROR] Missing input file.')
        return

    # Rotate nodes.
    global run_nodes
    run_nodes = all_nodes[opt.first_node:] + all_nodes[:opt.first_node]

    command.FANCY_SEEK = opt.fancy_seek
    server.KEEP_BALANCE_ORDER = opt.balance_order

    flavors = []
    for fl, name in zip(opt.flavor, letters()):
        b, _, res = fl.partition(':')
        res = res.split('x') if res else None

        flavors.append(Flavor(name, bv=b, res=res))
    opt.flavor = flavors

    if not opt.nodes:
        opt.nodes = len(run_nodes)

    if not opt.parts:
        opt.parts = opt.nodes

    print('File:', opt.input)
    print('Repeat:', opt.times, 'times')
    print('Log:', opt.log)
    print('Flavors:', opt.flavor)
    print('Nodes: {0.nodes} | Parts: {0.parts} | Threads: {0.threads}'.format(opt))
    print('Nodes data:')
    print(*('\t{0}:{1}'.format(*i) for i in run_nodes[:opt.nodes]), sep='\n')
    if opt.fancy_seek:
        print('Using fancy seek.')
    if opt.remove:
        print('All temporary files will be removed.')
    if opt.balance:
        print('Load balancing is on.')

    for t in range(opt.times):
        print('Run #{0}... '.format(t + 1), end='')
        sys.stdout.flush()
        time = _cluster_run(opt)
        print('-> {0:.2f} sec'.format(time))
    print()


def _cluster_run(opt):
    video = Transcoder(opt.input, opt.flavor)

    timer = Time().add('Start')

    video.probe()
    timer.add('Probe time')

    video.separate()  # LOCAL
    timer.add('Get audio')

    # Split
    cmds = video.split(opt.parts, threads=opt.threads, runner=None)
    nodes = run_nodes[:opt.nodes]
    timer.add('Split information')

    data = server.run(nodes, cmds, opt.balance)
    timer.add('Split running')

    video.join(opt.remove)  # LOCAL
    timer.add('Join')
    timer.add('Total time')

    info = timer.info()

    with open(opt.log, 'a') as f:
        f.write('\n---------------------------\n')
        f.write('Filename: %s\n' % video.filename)
        f.write('Nodes: %s\n' % opt.nodes)
        f.write('Parts: %s\n' % opt.parts)
        f.write('Threads: %s\n' % opt.threads)
        f.write('Flavors: %s\n' % video.flavors)
        f.write('::: Time :::\n')
        f.write(info)
        f.write('\nData:\n')
        f.write(str(data))

    return timer.get(-1)


def probe(opt):
    opt, _ = opt
    if not opt.input:
        print('[ERROR] Missing input file.')
        return
    data = Transcoder(opt.input).probe()
    pprint.pprint(data)
