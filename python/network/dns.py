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

import math
import random
import socket
import struct

class WBuffer():
    def __init__(self):
        self.buffer = []
        self.position = 0
    
    def __bytes__(self):
        return b''.join(self.buffer)
    
    def put_byte(self, byte):
        self.position += 1
        self.buffer.append(bytes([byte]))
    
    def put_bytes(self, bytes):
        self.position += len(bytes)
        self.buffer.append(bytes)

class RBuffer():
    def __init__(self, buffer):
        self.buffer = buffer
        self.position = 0
    
    def get_byte(self):
        self.position += 1
        return self.buffer[self.position - 1]
    
    def get_bytes(self, length):
        self.position += length
        return self.buffer[self.position - length:self.position]

def partition(message, blocksize):
    position, parts = 0, []
    for block in range(1, math.ceil(len(message) / blocksize) + 1):
        parts.append(message[position:block * blocksize])
        position = block * blocksize
    return parts

class DNSType():
    A = 1           # a host address
    NS = 2          # an authoritative name server
    MD = 3          # a mail destination (Obsolete - use MX)
    MF = 4          # a mail forwarder (Obsolete - use MX)
    CNAME = 5       # the canonical name for an alias
    SOA = 6         # marks the start of a zone of authority
    MB = 7          # a mailbox domain name (EXPERIMENTAL)
    MG = 8          # a mail group member (EXPERIMENTAL)
    MR = 9          # a mail rename domain name (EXPERIMENTAL)
    NULL = 10       # a null RR (EXPERIMENTAL)
    WKS = 11        # a well known service description
    PTR = 12        # a domain name pointer
    HINFO = 13      # host information
    MINFO = 14      # mailbox or mail list information
    MX = 15         # mail exchange
    TXT = 16        # text strings
    
    AXFR = 252      # a request for a transfer of an entire zone
    MAILB = 253     # a request for mailbox-related records (MB, MG or MR)
    MAILA = 254     # a request for mail agent RRs (Obsolete - see MX)
    ALL = 255       # a request for all records

class DNSClass():
    IN = 1          # the Internet
    CS = 2          # the CSNET class (Obsolete - used only for examples in some obsolete RFCs)
    CH = 3          # the CHAOS class
    HS = 4          # Hesiod [Dyer 87]

    ANY = 255       # any class

class DNS():
    MODE_QUERY = 0
    MODE_RESPONSE = 1
    
    OPCODE_QUERY = 0        # a standard query (QUERY)
    OPCODE_IQERY = 1        # an inverse query (IQUERY)
    OPCODE_STATUS = 2       # a server status request (STATUS)
    
    RD_NO_RECURSION = 0
    RD_RECURSION = 1
    
    RCODE_NO = 0            # no error condition
    RCODE_FORMAT = 1        # Format error - The name server was unable to interpret the query.
    RCODE_SERVER = 2        # Server failure - The name server was unable to process this query
                            # due to a problem with the name server.
    RCODE_NAME = 3          # Name Error - Meaningful only for responses from an authoritative name
                            # server, this code signifies that the domain name referenced in the query
                            # does not exist.
    RCODE_IMPLEMENTED = 4   # Not Implemented - The name server does not support the requeste
                            # kind of query.
    RCODE_REFUSED = 5       # Refused - The name server refuses to perform the specified operation for
                            # policy reasons.  For example, a name server may not wish to provide the
                            # information to the particular requester, or a name server may not wish to perform
                            # a particular operation (e.g., zone transfer) for particular data.
    
    HEADER = struct.Struct('! H H H H H H')
    QUESTION = struct.Struct('! H H')
    POINTER = struct.Struct('! H')
    RECORD = struct.Struct('! H H L H')
    
    def __init__(self, mode, number=None, headers={}):
        self.mode = mode
        self.number = random.randint(0, 65535) if number is None else number
        self.headers = headers
        self.questions = []
        self.answers = []
        self.authorities = []
        self.additionals = []
        
    def __bytes__(self):
        buffer, names = WBuffer(), {}
        def name(name):
            labels, pointer = [label.strip() for label in name.split('.') if label], None
            for number, label in enumerate(labels):   
                name, label = '.'.join(labels[number:]), label.encode('idna')
                if name in names:
                    pointer = names[name]
                    buffer.put_bytes(self.POINTER.pack(pointer | 0xC000))
                    break
                else:
                    if buffer.position < 0x3FFF:
                        names[name] = buffer.position
                    buffer.put_byte(len(label))
                    buffer.put_bytes(label)
            if pointer is None:
                buffer.put_bytes(b'\x00')
        
        def string(string):
            buffer.put_bytes(b''.join([struct.pack('! B', len(block)) + block.encode('idna') for block in partition(string, 63)]))
        
        def question(qname, qtype, qclass):
            name(qname)
            buffer.put_bytes(self.QUESTION.pack(qtype, qclass))
        
        def record_a(rdata):
            buffer.put_bytes(socket.inet_aton(rdata))
        
        def record_txt(rdata):
            string(rdata)
        
        def record_cname(rdata):
            name(rdata)
            
        def record_ns(rdata):
            name(rdata)
        
        table = {DNSType.A: record_a, DNSType.TXT: record_txt,
                 DNSType.CNAME: record_cname, DNSType.NS: record_ns}
        
        def record(rname, rtype, rclass, rttl, rdata):
            name(rname)
            header = len(buffer.buffer)
            buffer.put_bytes(b'\x00' * 10)
            position = buffer.position
            if rtype in table:
                table[rtype](rdata)
            else:
                buffer.put_bytes(rdata)
            rlength = buffer.position - position
            buffer.buffer[header] = self.RECORD.pack(rtype, rclass, rttl, rlength)              
        
        buffer.put_bytes(self.HEADER.pack(self.number,
                                          ((self.mode & 1) << 15 |
                                           (self.headers.get('opcode', 0) & 15) << 11 |
                                           (self.headers.get('aa', 0) & 1) << 10 |
                                           (self.headers.get('tc', 0) & 1) << 9 |
                                           (self.headers.get('rd', 0) & 1) << 8 |
                                           (self.headers.get('ra', 0) & 1) << 7 |
                                           (self.headers.get('z', 0) & 7) << 4 |
                                           (self.headers.get('rcode', 0) & 15)),
                                          len(self.questions), len(self.answers),
                                          len(self.authorities), len(self.additionals)))
        for qname, qtype, qclass in self.questions:
            question(qname, qtype, qclass)
        for rname, rtype, rclass, rttl, rdata in self.answers:
            record(rname, rtype, rclass, rttl, rdata)
        for rname, rtype, rclass, rttl, rdata in self.authorities:
            record(rname, rtype, rclass, rttl, rdata)
        for rname, rtype, rclass, rttl, rdata in self.additionals:
            record(rname, rtype, rclass, rttl, rdata)
        return bytes(buffer)
    
    @classmethod
    def parse(cls, buffer):
        def name():
            size, labels = buffer.get_byte(), []
            while size:
                if size & 0xc0 == 0xc0:
                    position, buffer.position = buffer.position, ((size << 8) | buffer.get_byte()) & ~0xC000
                    labels.append(name())
                    buffer.position, size = position + 1, 0
                else:
                    labels.append(buffer.get_bytes(size).decode('idna'))
                    size = buffer.get_byte()
            return '.'.join(labels)
        
        def string(length):
            size, parts, read = True, [], 0
            while size and read < length:
                size = buffer.get_byte()
                parts.append(buffer.get_bytes(size).decode('idna'))
                read += size + 1
            return ''.join(parts)
        
        def question():
            qname = name()
            qtype, qclass = cls.QUESTION.unpack(buffer.get_bytes(4))
            return qname, qtype, qclass
        
        def record_a(rlength):
            return socket.inet_ntoa(buffer.get_bytes(rlength))
        
        def record_txt(rlength):
            return string(rlength)
        
        def record_cname(rlength):
            return name()
        
        def record_ns(rlength):
            return name()
        
        table = {DNSType.A: record_a, DNSType.TXT: record_txt,
                 DNSType.CNAME: record_cname, DNSType.NS: record_ns}
        
        def record():
            rname = name()
            rtype, rclass, rttl, rlength = cls.RECORD.unpack(buffer.get_bytes(10))
            if rtype in table:
                rdata = table[rtype](rlength)
            else:
                rdata = buffer.get_bytes(rlength)
            return rname, rtype, rclass, rttl, rdata
                
        number, flags, qcount, acount, nscount, arcount = cls.HEADER.unpack(buffer.get_bytes(12))
        mode, opcode, aa, tc, rd, ra, z, rcode = ((flags >> 15) & 1,
                                                  (flags >> 11) & 15,
                                                  (flags >> 10) & 1,
                                                  (flags >> 9) & 1,
                                                  (flags >> 8) & 1,
                                                  (flags >> 7) & 1,
                                                  (flags >> 4) & 7,
                                                  (flags >> 0) & 15)
        headers = {'opcode': opcode, 'aa': aa, 'tc': tc, 'rd': rd, 'ra': ra, 'z': z, 'rcode': rcode}
        dns = DNS(mode, number, headers)
        for i in range(qcount):
            dns.questions.append(question())
        for i in range(acount):
            dns.answers.append(record())
        for i in range(nscount):
            dns.authorities.append(record())
        for i in range(arcount):
            dns.additionals.append(record())
        return dns
       
    def add_question(self, qname, qtype, qclass):
        self.questions.append((qname, qtype, qclass))
    
    def add_answer(self, rname, rtype, rclass, rttl, rdata):
        self.answers.append((rname, rtype, rclass, rttl, rdata))
    
    def add_authority(self, rname, rtype, rclass, rttl, rdata):
        self.authorities.append((rname, rtype, rclass, rttl, rdata))
    
    def add_additional(self, rname, rtype, rclass, rttl, rdata):
        self.additionals.append((rname, rtype, rclass, rttl, rdata))
    
class DNSQuery(DNS):
    def __init__(self, number=None, headers={}):
        super().__init__(self.MODE_QUERY, number, headers)

class DNSResponse(DNS):
    def __init__(self, number=None, headers={}):
        super().__init__(self.MODE_RESPONSE, number, headers)

def pack_tcp(query):
    query = bytes(query)
    return struct.pack('! H', len(query)) + query