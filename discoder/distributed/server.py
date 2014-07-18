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
import multiprocessing
import multiprocessing.dummy
import socket
import threading

from discoder.distributed import send_data, get_data
from discoder.lib.helper import star

__author__ = 'jb'

QUEUE_LOCK = threading.Lock()
KEEP_BALANCE_ORDER = False


def load_client(client, cmd):
    """ Open socket and write command to be executed remotely
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(client)
    send_data(s, cmd)
    out = get_data(s)
    s.close()

    return out


class CommandInfo(object):
    """ Keep track of position of command after its execution
    """
    def __init__(self, pos, data):
        self.pos = pos
        self.data = data


class LoadBalancer(object):
    def __init__(self, queue):
        self.queue = queue

    def run(self, client, num):
        done = []
        lock = threading.Lock()

        def queue_run(n):
            with lock:
                done_thread = []
                done.append(done_thread)
            while True:
                try:
                    with QUEUE_LOCK:
                        cmd = self.queue.get_nowait()
                except Exception:
                    break
                res = load_client(client, [cmd.data])[0]
                done_thread.append([cmd.pos, res])

        ths = []
        for x in range(num):
            th = threading.Thread(target=queue_run, args=(x,))
            th.daemon = True
            th.start()
            ths.append(th)
        for th in ths:
            th.join()

        return done


def list_numeric_order(data):
    """ Convert a list of balance outputs and put then in numerical segment order.
        [
            [
                [ [1, X1], [3, X3] ],
                [ [0, X0], [5, X5] ],
            ],
            [
                [ [2, X2], [7, X7] ],
                [ [4, X4], [6, X6] ],
            ],
        ]
        Output:
        [X0, X1, X2, X3, X4, X5, X6, X7]
    :param data: 4-Dimensional list
    :return: list
    """
    dic = {}
    for d in data:
        d = [x for sub in d for x in sub]
        dic.update(d)
    return [val for key, val in sorted(dic.items())]


def run(nodes, args, balance=False):
    """ Connect to clients using multiple processes.
    """
    #import pprint
    #print('Connecting to nodes:')
    #print(*('\t{0}:{1}'.format(*i) for i in nodes), sep='\n')
    #pprint.pprint(args, width=200)
    #print('Command:', len(args))

    nnodes = len(nodes)
    pool = multiprocessing.dummy.Pool(nnodes)
    if balance:
        args = [CommandInfo(i, x) for i, x in enumerate(args)]
        queue = multiprocessing.Queue(maxsize=len(args))
        for el in args:
            queue.put(el, block=True)
        parts = [balance for _ in range(nnodes)]
        out = pool.map(star(LoadBalancer(queue).run), zip(nodes, parts))
        if not KEEP_BALANCE_ORDER:
            out = list_numeric_order(out)
    else:
        n = len(args) // nnodes
        # noinspection PyArgumentList
        parts = [args[i:i+n] for i in range(0, n * nnodes, n)]
        out = pool.map(star(load_client), zip(nodes, parts))

    #pool.close()
    return out
