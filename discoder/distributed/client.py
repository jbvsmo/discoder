import SocketServer
from multiprocessing import Pool
import time
from discoder.distributed import get_data, send_data
from discoder.proc import run_local


__author__ = 'jb'


class ClientTCPHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        """ Get input data with lenght + '\n' and process it
        """
        print('Conected...')

        data = get_data(self.request)
        out = Pool(len(data)).map(run_proc, data)
        send_data(self.request, out)

        print('Done!')

def start(port):
    """ Open socket server and waits to remote command.
    """
    host = '0.0.0.0'
    server = SocketServer.TCPServer((host, port), ClientTCPHandler)
    try:
        print('Running client on {0}:{1}'.format(host, port))
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()

def run_proc(data):
    """ Measure time and run process
    """
    a = time.time()
    run_local(data)
    b = time.time()
    return b-a