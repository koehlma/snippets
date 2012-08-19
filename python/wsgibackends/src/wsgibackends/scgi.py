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

import io
import socketserver
import wsgiref.util

class SCGIServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    class _Handler(socketserver.BaseRequestHandler):
        def handle(self):
            length = ''
            while not length.endswith(':'):
                length += self.request.recv(1).decode('ascii')
            length = int(length[:-1])
            rfile = self.request.makefile('rb', -1)
            wfile = self.request.makefile('wb', 0)
            environ = rfile.read(length).decode('latin1').split('\x00')
            environ = dict([(environ[i], environ[i + 1]) for i in range(0, len(environ) - 2, 2)])
            environ['wsgi.errors'] = io.StringIO()
            environ['wsgi.file_wrapper'] = wsgiref.util.FileWrapper
            environ['wsgi.input'] = rfile
            environ['wsgi.multiprocess'] = False
            environ['wsgi.multithread'] = True
            environ['wsgi.run_once'] = False
            environ['wsgi.version'] = (1, 0)
            if environ.get('HTTPS', 'off') in ('on', '1'):
                environ['wsgi.url_scheme'] = 'https'
            else:
                environ['wsgi.url_scheme'] = 'http'
            
            def start_response(status, headers):
                headers = ['{}: {}'.format(name, value) for name, value in headers] 
                headers.append('Status: {}'.format(status))
                wfile.write(('\r\n'.join(headers) + '\r\n\r\n').encode('latin1'))
            
            for chunk in self.server.application(environ, start_response):
                wfile.write(chunk)
        
    def __init__(self, host, port, application, reuseaddr=False):
        self.application = application
        self.allow_reuse_address = reuseaddr
        super().__init__((host, port), self._Handler)

if __name__ == '__main__':
    from wsgiref.simple_server import demo_app

    scgi_server = SCGIServer('0.0.0.0', 8888, demo_app, True)
    scgi_server.serve_forever()