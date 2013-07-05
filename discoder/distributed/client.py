try:
    import SocketServer as socketserver
except ImportError:
    import socketserver
from multiprocessing.dummy import Pool
import time
from discoder.distributed import get_data, send_data
from discoder.proc import run_local


__author__ = 'jb'

TH_COUNT = 0

class ClientTCPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        """ Get input data with lenght + '\n' and process it
        """
        global TH_COUNT
        #print('Conected...')
        TH_COUNT += 1
        print('TH_COUNT in = ' + str(TH_COUNT))
        data = get_data(self.request)
        pool = Pool(len(data))
        out = pool.map(run_proc, data)
        pool.close()
        print(out)
        send_data(self.request, out)
        TH_COUNT -= 1
        print('TH_COUNT out = ' + str(TH_COUNT))

        #print('Done!')


def start(port):
    """ Open socket server and waits to remote command.
    """
    host = '0.0.0.0'
    server = None
    while True:
        try:
            server = socketserver.ThreadingTCPServer((host, port), ClientTCPHandler)
        except IOError:
            print('Trying to listen on {0}:{1}'.format(host, port))
            time.sleep(5)
        else:
            break

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
