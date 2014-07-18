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

import json

__author__ = 'jb'

RECV_TIMEOUT = None
VERBOSE = True

DEFAULT_PORT = 7001
ENCODING = 'utf-8'
RETRY = 10

def get_data(socket):
    """ Get input data with lenght + '\n' as header
    """
    if RECV_TIMEOUT:
        socket.settimeout(RECV_TIMEOUT)
    val = None
    r = 0
    try:
        for r in range(RETRY):
            val = socket.recv(64).decode(ENCODING)
            if val:
                break
        header, data = val.split('\n', 1)
    except (ValueError, TypeError) as e:
        raise Exception('Invalid data received: {0!r}\n '
                        'runs: {1}\n err: {2!r}'.format(val, r, e))
    size = int(header)

    while len(data) < size:
        data += socket.recv(1024).decode(ENCODING)
        if not data:
            break
    return json.loads(data)


def send_data(socket, data):
    data = json.dumps(data)
    data = '{0}\n{1}'.format(len(data), data)
    socket.sendall(data.encode(ENCODING))


def parse_address(addr, default=DEFAULT_PORT):
    """ Split server address in name and port or add a port if there's none
    """
    name, _, port = addr.strip().partition(':')
    port = int(port) if port else default
    return name, port
