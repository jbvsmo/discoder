from __future__ import print_function
import multiprocessing
import multiprocessing.dummy
import socket
import threading

from discoder.distributed import send_data, get_data
from discoder.lib.helper import star

__author__ = 'jb'


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
        done = {}
        def queue_run():
            while True:
                try:
                    cmd = self.queue.get_nowait()
                except Exception:
                    break
                done[cmd.pos] = load_client(client, [cmd.data])

        ths = []
        for x in range(num):
            th = threading.Thread(target=queue_run)
            th.daemon = True
            th.start()
            ths.append(th)
        for th in ths:
            th.join()

        return done


def dicts_to_list(dicts):
    """ Convert a list of dictionaries of numbers to a single list
        of their values sorted by keys. Repeated keys will be overwritten.
    :param dicts: list of dicts
    :return: list
    """
    dic = {}
    for d in dicts:
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
    pool = multiprocessing.dummy.Pool()
    if balance:
        args = [CommandInfo(i, x) for i, x in enumerate(args)]
        queue = multiprocessing.Queue()
        for el in args:
            queue.put(el)
        parts = [balance for _ in range(nnodes)]
        out = pool.map(star(LoadBalancer(queue).run), zip(nodes, parts))
        return dicts_to_list(out)

    n = len(args) // nnodes
    parts = [args[i:i+n] for i in range(0, n * nnodes, n)]
    return pool.map(star(load_client), zip(nodes, parts))
