#!/usr/bin/env python3
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

import sys
import struct

boot_img = struct.Struct('8s 2I 2I 2I 4I 16s 512s 8I')

def main(filename):
    with open(filename, 'rb') as input:
        header = boot_img.unpack(input.read(boot_img.size))
    print('Magic    : {}'.format(header[0]))
    print('Kernel   : {}, {}'.format(header[1], header[2]))
    print('Ramdisk  : {}, {}'.format(header[3], header[4]))
    print('Second   : {}, {}'.format(header[5], header[6]))
    print('Tagsaddr : {}'.format(header[7]))
    print('Pagesize : {}'.format(header[8]))
    print('Unused   : {}, {}'.format(header[9], header[10]))
    print('Name     : {}'.format(header[11]))
    print('Cmdline  : {}'.format(header[12]))
    print('Id       : {}'.format(', '.join(map(str, header[13:]))))
    
    kernel_size = header[1]
    ramdisk_size = header[3]
    second_size = header[5]
    page_size = header[8]
    
    n = (kernel_size + page_size - 1) / page_size
    m = (ramdisk_size + page_size - 1) / page_size
    o = (second_size + page_size - 1) / page_size
    
    with open(filename, 'rb') as input:
        print('Extracting Header...')
        with open('header.img', 'wb') as output:
            output.write(input.read(page_size))
        print('Extracting Kernel...')
        with open('kernel.img', 'wb') as output:
            output.write(input.read(n * page_size))
        print('Extracting Ramdisk...')
        with open('ramdisk.img', 'wb') as output:
            output.write(input.read(m * page_size))
        print('Extracting Second...')
        with open('second.img', 'wb') as output:
            output.write(input.read(o * page_size))

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('usage: %s <image file>' % (sys.argv[0]))
    else:
        main(sys.argv[1])
