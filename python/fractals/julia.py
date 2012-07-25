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

import argparse
import collections
import struct

F = lambda z, c: z ** 2 + c     # julia base function
ITERATIONS = 255                # number of iterations

RGB = collections.namedtuple('RGB', ['red', 'green', 'blue'])

def gradient(from_rgb, to_rgb, length=10):
    """
    Generates a gradient from `from_rgb` to `to_rgb` with `length` steps and
    yields color by color.
    """
    diff_rgb = RGB(to_rgb.red - from_rgb.red, to_rgb.green - from_rgb.green, to_rgb.blue - from_rgb.blue)
    length = length - 1
    for i in range(length + 1):
        yield RGB(int(from_rgb.red + diff_rgb.red / length * i), int(from_rgb.green + diff_rgb.green / length * i), int(from_rgb.blue + diff_rgb.blue / length * i))

def julia(z, c, f=F, r=2, iterations=ITERATIONS):
    """
    Generates the Julia fractal.
    """ 
    for i in range(iterations):
        if abs(z) > r: break
        z = f(z, c)
    return i

# gradient for fancy colors 
colors = (list(gradient(RGB(0, 0, 0), RGB(0, 0, 255), int(ITERATIONS * 0.1))) + 
          list(gradient(RGB(0, 0, 255), RGB(0, 255, 255), int(ITERATIONS * 0.2))) +
          list(gradient(RGB(0, 255, 255), RGB(0, 255, 0), int(ITERATIONS * 0.3))) +
          list(gradient(RGB(0, 255, 0), RGB(255, 255, 255), int(ITERATIONS * 0.4 + 1))))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Render some beautiful Julia fractals.')
    parser.add_argument('output', help='output image')
    parser.add_argument('-C', default=[-0.8, 0.2], type=float,
                        help='julia\'s complex parameter (c = f1 + f2)', nargs=2, metavar='f')
    parser.add_argument('--width', default=1500,
                        help='image width', type=int)
    parser.add_argument('--scale', default=400,
                        help='scale the image', type=int)


    arguments = parser.parse_args()
    
    c, width, scale = complex(*arguments.C), arguments.width, arguments.scale
    
    print('Generating Julia Fractal:')
    print('    c         : {:f}'.format(c))
    print('    f         : z ^ 2 + c')
    print('    iterations: 255')
    print('    scale     : {}'.format(scale))
    print('    width     : {}'.format(width))
    with open(arguments.output, 'wb') as output:
        # bmp header
        output.write(b'BM' + struct.pack('<QIIHHHH', width * width * 3 + 26, 26, 12, width, width, 1, 24))
        # scaling
        values = []
        for i in range(int(-(width + 9) / 2), int((width + 9) / 2)):
            values.append(i / scale)
        # total steps    
        total = arguments.width ** 2
        # rendering
        for y in range(width):
            for x in range(width):
                current = width * y + x
                print('\r    progress  : {:.2f}% ({}/{})'.format(current / total * 100, current, total), end='')
                color = colors[julia(complex(values[x], values[y]), c)]
                output.write(struct.pack('BBB', color.blue, color.green, color.red))
        print()