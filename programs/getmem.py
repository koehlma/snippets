#!/usr/bin/env python2
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
import os.path
import subprocess

def wait_for_promt(gdb):
    output = ''
    while not output.endswith('(gdb)'):
        output += gdb.stdout.read(1)
        
def read(pid, output):
    with open('/proc/%s/maps' % (pid), 'rb') as maps:
        addresses = []
        for line in maps.readlines():
            addresses.append(line.split().pop(0).split('-'))
    gdb = subprocess.Popen(['/usr/bin/gdb', '--pid', pid],
                           stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    wait_for_promt(gdb)
    for address in addresses:
        print('%s-%s -> %s'  % (address[0], address[1],
                                os.path.join(output, '%s-%s' % (address[0], address[1]))))
        gdb.stdin.write('dump memory %s 0x%s 0x%s\n' % (os.path.join(output, '%s-%s' % (address[0], address[1])),
                                                            address[0], address[1]))
        wait_for_promt(gdb)

if __name__ == '__main__':
    if not len(sys.argv) == 3:
        print('usage: %s <pid> <output directory>' % (sys.argv[0]))
    elif not os.path.isdir(sys.argv[2]):
        print('please give a valid directory')
    elif not os.path.isfile('/proc/%s/maps' % (sys.argv[1])):
        print('please give a valid pid')
    else:
        read(sys.argv[1], sys.argv[2])
