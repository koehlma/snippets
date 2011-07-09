#!/usr/bin/env python
# -*- coding:utf-8 -*-

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import print_function

import sys
import socket
import signal
import re

IP_RE = re.compile(r'^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$')

class Timeout(Exception):
    pass

def raise_timeout(signum, frame):
    raise Timeout()

def is_integer(string):
    try:
        int(string)
        return True
    except ValueError:
        return False

def scan_ports(ip, min_port, max_port):
    ports = range(min_port, max_port + 1)
    openports = []
    closedports = 0
    for port in ports:
        print('\ropen ports: %i / closed ports: %i / current: %i' % (len(openports), closedports, port), end='')
        connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            signal.alarm(1)
            connection.connect((ip, port))
            signal.alarm(0)
            openports.append(port)
        except socket.error , Timeout:
            closedports += 1
        connection.close()
    if openports:
        print('\nopen ports: %s' % (', '.join([str(port) for port in openports])))
    else:
        print('\nsorry, no open ports found in the given range')

if __name__ == '__main__':
    signal.signal(signal.SIGALRM, raise_timeout)
    if not len(sys.argv) == 4:
        print('usage: %s <ip address> <start port> <end port>' % (sys.argv[0]))
    elif not IP_RE.match(sys.argv[1]):
        print('please give a valid ip address')
    elif not is_integer(sys.argv[2] or not is_integer(sys.argv[3])):
        print('port numbers should be integer')
    elif int(sys.argv[2]) > int(sys.argv[3]):
        print('start port must be smaller than end port')     
    else:
        scan_ports(sys.argv[1], int(sys.argv[2]), int(sys.argv[3]))