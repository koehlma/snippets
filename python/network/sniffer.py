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

import socket
import struct
import textwrap
import time

class Pcap():
    def __init__(self, filename, link_type=1):
        self.pcap = open(filename, 'wb')
        self.pcap.write(struct.pack('@ I H H i I I I', 0xa1b2c3d4, 2, 4, 0, 0,
                                    65535, link_type))
    
    def write(self, packet):
        ts_sec, ts_usec = map(int, str(time.time()).split('.'))
        length = len(packet)
        self.pcap.write(struct.pack('@ I I I I', ts_sec, ts_usec, length, length))
        self.pcap.write(packet)
    
    def close(self):
        self.pcap.close()

def format_multiline(prefix, string, length=80):
    length = length - len(prefix)
    if isinstance(string, bytes):
        string = ''.join(r'\x{:02x}'.format(byte) for byte in string)
        if length % 2: length -= 1
    return '\n'.join([prefix + line
                      for line in textwrap.wrap(string, length)])

def mac(address):
    return (':'.join(map('{:02x}'.format, address))).upper()

def ethernet_frame(data):
    destination, source, protocol = struct.unpack('! 6s 6s H', data[:14])
    return mac(destination), mac(source), socket.htons(protocol), data[14:]

def ipv4(address):
    return '.'.join(map(str, address))

def ipv4_packet(data):
    version_header_length = data[0]
            
    version = version_header_length >> 4
    header_length = (version_header_length & 15) * 4

    ttl, protocol, source, target = struct.unpack('! 8x B B 2x 4s 4s', data[:20])
    
    return (version, header_length, ttl, protocol, ipv4(source), ipv4(target),
            data[header_length:])

def icmp_packet(data):
    type, code, checksum = struct.unpack('! B B H', data[:4])
    return type, code, checksum, data[4:]  

def tcp_segment(data):
    (source_port, destination_port, sequence, acknowledgment,
     offset_reserved_flags) = struct.unpack('! H H L L H', data[:14])
    
    offset = (offset_reserved_flags >> 12) * 4
    flag_urg = (offset_reserved_flags & 32) >> 5
    flag_ack = (offset_reserved_flags & 16) >> 4
    flag_psh = (offset_reserved_flags & 8) >> 3
    flag_rst = (offset_reserved_flags & 4) >> 2
    flag_syn = (offset_reserved_flags & 2) >> 1
    flag_fin = offset_reserved_flags & 1
    
    return (source_port, destination_port, sequence, acknowledgment, flag_urg,
            flag_ack, flag_psh, flag_rst, flag_syn, flag_fin, data[offset:])

def udp_segment(data):
    source_port, destination_port, length = struct.unpack('! H H 2x H', data[:8])
    return source_port, destination_port, length, data[8:]

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) == 2:
        pcap = Pcap(sys.argv[1])
    else:
        pcap = None
    
    connection = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(3))
    
    while True:
        data, address = connection.recvfrom(65535)
        
        if pcap is not None: pcap.write(data)
        
        destination, source, protocol, data = ethernet_frame(data)
        
        print('Ethernet Frame:')
        print(('| - Destination: {}, Source: {}, Protocol: {}')
              .format(destination, source, protocol))
        
        if protocol == 8:
            (version, header_length, ttl, protocol, source, target,
             data) = ipv4_packet(data)
            
            print('| - IPv4 Packet:')
            print(('    | - Version: {}, Header Length: {}, TTL: {},'
                   ).format(version, header_length, ttl))
            print(('    | - Protocol: {}, Source: {}, Target: {}'
                   ).format(protocol, source, target))
            
            if protocol == 1:
                type, code, checksum, data = icmp_packet(data)
                print('    | - ICMP Packet:')
                print(('        | - Type: {}, Code: {}, Checksum: {},'
                       ).format(type, code, checksum))
                print('        | - Data:')
                print(format_multiline('            | - ', data))
                
            elif protocol == 6:
                (source_port, destination_port, sequence, acknowledgment,
                 flag_urg, flag_ack, flag_psh, flag_rst, flag_syn, flag_fin,
                 data) = tcp_segment(data)
                print('    | - TCP Segment:')
                print(('        | - Source Port: {}, Destination Port: {}'
                       ).format(source_port, destination_port))
                print(('        | - Sequence: {}, Acknowledgment: {}'
                       ).format(sequence, acknowledgment))
                print('        | - Flags:')
                print(('             | - URG: {}, ACK: {}, PSH: {}, RST: {}, '
                       'SYN: {}, FIN:{}').format(flag_urg, flag_ack, flag_psh,
                                                 flag_rst, flag_syn, flag_fin))
                print('        | - Data:')
                print(format_multiline('            | - ', data))
            
            elif protocol == 17:
                source_port, destination_port, length, data = udp_segment(data)
                print('    | - UDP Segment:')
                print(('        | - Source Port: {}, Destination Port: {}, '
                       'Length: {}').format(source_port, destination_port, length))
                      
            else:
                print('    | - Data:')
                print(format_multiline('        | - ', data))
                                  
        else:
            print('| - Data:')
            print(format_multiline('    | - ', data))
        
        print()
        