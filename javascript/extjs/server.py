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

import bottle

@bottle.route('/')
def redirect():
    bottle.redirect('/loginform/index.html')

@bottle.route('/loginform/<path:path>')
def static(path):
    return bottle.static_file(path, root='./loginform/')

@bottle.route('/extjs/<path:path>')
def static(path):
    return bottle.static_file(path, root='./extjs/')

@bottle.route('/request/login', method='POST')
def login():
    username = bottle.request.forms.get('username')
    password = bottle.request.forms.get('password')
    if username == 'example' and password == 'example':
        return {'success': True}
    else:
        return {'success': False}

bottle.run(host='localhost', port=8080, debug=True)