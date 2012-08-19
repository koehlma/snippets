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
import functools
import io
import os
import socketserver
import select
import struct
import threading
import wsgiref.util

class FCGIServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    class _Handler(socketserver.StreamRequestHandler):
        VERSION = 1
    
        BEGIN_REQUEST = 1
        ABORT_REQUEST = 2
        END_REQUEST = 3
        PARAMS = 4
        STDIN = 5
        STDOUT = 6
        STDERR = 7
        DATA = 8
        GET_VALUES = 9
        GET_VALUES_RESULT = 10
        UNKNOWN_TYPE = 11
        MAXTYPE = UNKNOWN_TYPE
        
        NULL_REQUEST_ID = 0
        
        KEEP_CONN = 1
        
        RESPONDER = 1
        AUTHORIZER = 2
        FILTER = 3
        
        REQUEST_COMPLETE = 0
        CANT_MPX_CONN = 1
        OVERLOADED = 2
        UNKNOWN_ROLE = 3
        
        RECORD = struct.Struct('! B B B B B B B B')
        
        CONTENT_BEGIN_REQUEST = struct.Struct('! B B B 5s')
        CONTENT_END_REQUEST = struct.Struct('! B B B B B 3s')
        CONTENT_UNKNOWN_TYPE = struct.Struct('! B 7s')
        
        _Record = collections.namedtuple('Record', ['version', 'type', 'request_id_b1', 'request_id_b0', 'content_length_b1', 'content_length_b0', 'padding_length', 'reserved'])

        _ContentBeginRequest = collections.namedtuple('ContentBeginRequest', ['role_b1', 'role_b0', 'flags', 'reserved'])
        
        class _Request():
            class _Stdin():
                def __init__(self):
                    read, write = os.pipe()
                    self.rfile = os.fdopen(read, 'rb', 0)
                    self.wfile = os.fdopen(write, 'wb', 0)
                    for name in ('fileno', 'read', 'readline', 'readlines', 'seek', 'tell', 'truncate', '__iter__'):
                        setattr(self, name, functools.partial(self._redict, name))
                
                def _redict(self, name, *args, **kwargs):
                    return getattr(self.rfile, name)(*args, **kwargs)
                    
                def write(self, content):
                    self.wfile.write(content)
                                            
            def __init__(self, handler, request_id, role, flags):
                self.handler = handler
                self.request_id = request_id
                self.role = role
                self.flags = flags
                self.environ = {}
                self.lock = threading.Lock()
                self.stdin = self._Stdin()
                self.mapping = {self.handler.PARAMS: self._record_params,
                                self.handler.STDIN: self._record_stdin}
                self.running = False
            
            def _record_params(self, content):
                position = 0
                while position < len(content):
                    name_len = content[position]
                    position += 1
                    if name_len & 128:
                        name_len = ((name_len & 127) << 24) + (content[position] << 16) + (content[position + 1] << 8) + content[position + 2]
                        position += 3
                    value_len = content[position]
                    position += 1
                    if value_len & 128:
                        value_len = ((name_len & 127) << 24) + (content[position] << 16) + (content[position + 1] << 8) + content[position + 2]
                        position += 3
                    self.environ[content[position:position + name_len].decode('latin1')] = content[position + name_len:position + name_len + value_len].decode('latin1')
                    position += name_len + value_len
                
            def _record_stdin(self, content):
                self.stdin.write(content)
                if not self.running:
                    self.running = True
                    threading.Thread(target=self.run).start()
                        
            def handle_record(self, record, content):
                if record.type in self.mapping:
                    self.mapping[record.type](content)
            
            def write_record(self, type, content):
                length = len(content)
                padding = ((length + 7) & (0xFFFF - 7)) - length
                record = self.handler.RECORD.pack(self.handler.VERSION, type, self.request_id >> 8, self.request_id & 255, length >> 8, length & 255, padding, 0)
                with self.lock:
                    self.handler.wfile.write(record + content + padding * b'\x00')
            
            def run(self):
                self.environ['wsgi.errors'] = io.StringIO()
                self.environ['wsgi.file_wrapper'] = wsgiref.util.FileWrapper
                self.environ['wsgi.input'] = self.stdin
                self.environ['wsgi.multiprocess'] = False
                self.environ['wsgi.multithread'] = True
                self.environ['wsgi.run_once'] = False
                self.environ['wsgi.version'] = (1, 0)
                if self.environ.get('HTTPS', 'off') in ('on', '1'):
                    self.environ['wsgi.url_scheme'] = 'https'
                else:
                    self.environ['wsgi.url_scheme'] = 'http'
                                
                def start_response(status, headers):
                    headers = ['{}: {}'.format(name, value) for name, value in headers] 
                    headers.append('Status: {}'.format(status))
                    self.write_record(self.handler.STDOUT, ('\r\n'.join(headers) + '\r\n\r\n').encode('latin1'))
                 
                for chunk in self.handler.server.application(self.environ, start_response):
                    self.write_record(self.handler.STDOUT, chunk)
                
                self.write_record(self.handler.STDOUT, b'')
                # Why does this not work?
                self.write_record(self.handler.END_REQUEST, self.handler.CONTENT_END_REQUEST.pack(0, 0, 0, 0, 0, b'\x00\x00\x00'))
                del self.handler.requests[self.request_id]
                
        def _begin_request(self, request_id, content):
            begin_request = self._ContentBeginRequest(*self.CONTENT_BEGIN_REQUEST.unpack(content))
            self.requests[request_id] = self._Request(self, request_id, (begin_request.role_b1 << 8) + begin_request.role_b0, begin_request.flags)        
        
        def handle(self):
            self.requests = {}
            poller = select.epoll()
            poller.register(self.rfile, select.EPOLLIN | select.EPOLLPRI)
            while not self.server._BaseServer__shutdown_request:
                # for fd, event in poller.poll(0.5): # Why does this not work?
                record = self._Record(*self.RECORD.unpack(self.rfile.read(self.RECORD.size)))
                request_id = (record.request_id_b1 << 8) + record.request_id_b0
                content_length = (record.content_length_b1 << 8) + record.content_length_b0
                content = self.rfile.read(content_length)
                self.rfile.read(record.padding_length)
                if record.type == self.BEGIN_REQUEST:
                    self._begin_request(request_id, content)
                else:
                    if request_id in self.requests:
                        self.requests[request_id].handle_record(record, content)

    def __init__(self, host, port, application, reuseaddr=False):
        self.application = application
        self.allow_reuse_address = reuseaddr
        super().__init__((host, port), self._Handler)

if __name__ == '__main__':
    from wsgiref.simple_server import demo_app

    fcgi_server = FCGIServer('0.0.0.0', 8888, demo_app, True)
    fcgi_server.serve_forever()