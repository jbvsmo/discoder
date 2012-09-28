from __future__ import print_function
from multiprocessing import Pool
import pprint
import socket
from discoder.distributed import send_data, get_data

__author__ = 'jb'

def load_client(arguments):
    """ Open socket and write command to be executed remotely
    """
    client, cmd = arguments
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(client)

    send_data(s, cmd)
    out = get_data(s)
    s.close()

    return out


def run(nodes, args):
    """ Connect to clients using multiple processes.
    """
    print('Connecting to nodes:')
    print(*('\t{0}:{1}'.format(*i) for i in nodes), sep='\n')
    #pprint.pprint(args, width=200)
    print('Command:', len(args))

    pool = Pool(len(nodes))
    out = pool.map(load_client, zip(nodes, args))
    return out