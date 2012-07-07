#!/usr/bin/env python3
# -*- coding:utf-8 -*-
#
# Copyright (C) 2012, Maximilian Köhl <linuxmaxi@googlemail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import collections
import struct

WIDTH = 1500
SCALE = 1000
# Julia 1
#C = -0.8 + 0.2j
# Julia 2
C = -0 + 0.8j
# Julia 3
#C = -1 + 0j
F = lambda z, c: z ** 2 + c
ITERATIONS = 255
FILENAME = 'output.bmp'

RGB = collections.namedtuple('RGB', ['red', 'green', 'blue'])

def gradient(from_rgb, to_rgb, length=10):
    diff_rgb = RGB(to_rgb.red - from_rgb.red, to_rgb.green - from_rgb.green, to_rgb.blue - from_rgb.blue)
    length = length - 1
    for i in range(length + 1):
        yield RGB(int(from_rgb.red + diff_rgb.red / length * i), int(from_rgb.green + diff_rgb.green / length * i), int(from_rgb.blue + diff_rgb.blue / length * i))

def julia(z, c, f=lambda z, c: z ** 2 + c, r=2):
    for i in range(ITERATIONS):
        if abs(z) > r:
            break
        z = f(z, c)
    return i

def bmp(filename, height, width, f):    
    with open(filename, 'wb') as output:
        output.write(b'BM' + struct.pack('<QIIHHHH', width * height * 3 + 26, 26, 12, width, height, 1, 24))
        for color in f():
            output.write(struct.pack('BBB', color.blue, color.green, color.red))

colors = (list(gradient(RGB(0, 0, 0), RGB(0, 0, 255), int(ITERATIONS * 0.1))) + 
          list(gradient(RGB(0, 0, 255), RGB(0, 255, 255), int(ITERATIONS * 0.2))) +
          list(gradient(RGB(0, 255, 255), RGB(0, 255, 0), int(ITERATIONS * 0.3))) +
          list(gradient(RGB(0, 255, 0), RGB(255, 255, 255), int(ITERATIONS * 0.4 + 1))))

def generate(f=F):
    values = []
    for i in range(int(-(WIDTH + 9) / 2), int((WIDTH + 9) / 2)):
        values.append(i / SCALE)    
    total = WIDTH ** 2
    for y in range(WIDTH):
        for x in range(WIDTH):
            current = WIDTH * y + x
            print('\r{}/{} - {:.2f}%'.format(current, total, current / total * 100), end='')
            yield colors[julia(complex(values[x], values[y]), C)]
    print()
    
if __name__ == '__main__':
    bmp(FILENAME, WIDTH, WIDTH, generate)