import json

__author__ = 'jb'

RECV_TIMEOUT = None
VERBOSE = True

DEFAULT_PORT = 7001

def get_data(socket):
    """ Get input data with lenght + '\n' as header
    """
    if RECV_TIMEOUT:
        socket.settimeout(RECV_TIMEOUT)
    data = b''
    header, data = socket.recv(64).split('\n', 1)
    size = int(header)

    while len(data) < size:
        data += socket.recv(1024)
        if not data:
            break
    return json.loads(data)


def send_data(socket, data):
    data = json.dumps(data)
    data = '{0}\n{1}'.format(len(data), data)
    socket.sendall(data)


def parse_address(addr, default=DEFAULT_PORT):
    """ Split server address in name and port or add a port if there's none
    """
    name, _, port = addr.strip().partition(':')
    port = int(port) if port else default
    return name, port