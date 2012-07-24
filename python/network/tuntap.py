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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import fcntl
import os
import struct
import subprocess

class Device():
    MODE_TUN = 1
    MODE_TAP = 2
    
    def __init__(self, mode, name='', control='/dev/net/tun', mtu=1500):
        self.mode, self.control, self.file = mode, control, os.open(control, os.O_RDWR)
        self.name = fcntl.ioctl(self.file, 1074025674, struct.pack('16sH', name.encode('ascii'), self.mode))[:16].strip(b'\x00').decode('ascii')
        self.mtu = mtu
    
    @property
    def mtu(self):
        return self._mtu
    
    @mtu.setter
    def mtu(self, mtu):
        self.config(mtu=mtu)
     
    def read(self):
        return os.read(self.file, self.mtu)
    
    def write(self, data):
        os.write(self.file, data)
    
    def close(self):
        os.close(self.file)
    
    def up(self):
        subprocess.call(['ip', 'link', 'set', self.name, 'up'])
        
    def down(self):
        subprocess.call(['ip', 'link', 'set', self.name, 'down'])
    
    def config(self, address=None, netmask=None, network=None, broadcast=None, mtu=None, hwclass=None, hwaddr=None):
        command = ['ifconfig', self.name]
        if address is not None: command.append(address)
        if netmask is not None: command.extend(['netmask', netmask])
        if network is not None: command.extend(['network', network])
        if broadcast is not None: command.extend(['boradcast', broadcast])
        if mtu is not None:
            self._mtu = mtu
            command.extend(['mtu', str(mtu)])
        if hwclass is not None and hwaddr is not None:
            command.extend(['hw', hwclass, hwaddr])
        subprocess.call(command)

class TUNDevice(Device):
    def __init__(self, *args, **kwargs):
        super().__init__(self.MODE_TUN, *args, **kwargs)
        
class TAPDevice(Device):
    def __init__(self, *args, **kwargs):
        super().__init__(self.MODE_TAP, *args, **kwargs)