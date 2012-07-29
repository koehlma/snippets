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
import html
import json
import logging
import sys
import time
import traceback
import urllib.parse
import urllib.request

import bs4

class WikipediaBot():
    INFO = ('<h1>Interactive Note</h1>'
            '<p>View Wikipedia for free over <i>0.facebook.com</i>.</p>'
            '<h2>Commands</h2>'
            '<ul>'
            '    <li><b>get:$title</b> fetch any Wikipedia article</li>'
            '    <li><b>reset</b> reset the note</li>'
            '</ul>')
    
    def __init__(self, access_token, note_id):
        self.access_token, self.note_id = access_token, note_id
        self.active = False
        self.headers = {'User-Agent' : ('Mozilla/5.0 (X11; Linux x86_64; rv:14.'
                                        '0) Gecko/20100101 Firefox/14.0.1')}
        self.update('Interactive Note', self.INFO)
    
    def _command_get(self, page):
        url = ('http://de.wikipedia.org/wiki/{}?printable=yes'
               ).format(urllib.parse.quote(page))
        request = urllib.request.Request(url, headers=dict(self.headers))
        response = urllib.request.urlopen(request)
        soup = bs4.BeautifulSoup(response.read().decode('utf-8'))
        text = [self.INFO, '<h1>{}</h1>'.format(page)]
        for child in soup.find('div', id='mw-content-text'):
            if isinstance(child, bs4.Tag):
                if child.name in ('h1', 'h2', 'h3'):
                    heading = child.find('span', {'class' : 'mw-headline'})
                    text.append('<{tag}>{heading}</{tag}>'.format(tag=child.name, heading=heading.text))
                elif child.name == 'p':
                    text.append('<p>' + child.text + '</p>')
                elif child.name in ('ul', 'ol'):
                    text.append('<' + child.name + '>')
                    for item in child:
                        if isinstance(item, bs4.Tag):
                            text.append('<li>' + item.text + '</li>')
                    text.append('</' + child.name + '>')
        output = '\n'.join(text)[:40000]
        self.update('Interactive Note - Wikipedia - {}'.format(page),
                    output)     
    
    def _command_reset(self):
        self.update('Interactive Note', self.INFO)
    
    def process(self, comment):
        command, *arguments = comment.split(':')
        if hasattr(self, '_command_{}'.format(command)):
            try:
                getattr(self, '_command_{}'.format(command))(*arguments)
            except Exception as error:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                tb = ''.join(traceback.format_tb(exc_traceback))
                self.error(str(error), '<pre>' + tb + '</pre>')
        else:
            self.error('Unknown Command',
                       'Unknown command: "{}"'.format(command))
    
    def error(self, title, message):
        subject = 'Interactive Note - Error'
        self.update(subject, self.INFO + '<h1>' + 'Error - ' + title + '</h1>' +
                    message)         
    
    def comment(self):
        query = ('SELECT object_id, id, fromid, text, time FROM comment WHERE '
                 'object_id = \'{}\' ORDER BY time desc  LIMIT 1'
                 ).format(self.note_id)
        url = ('https://graph.facebook.com/fql?q={}&access_token={}'
               ).format(urllib.parse.quote_plus(query), self.access_token)
        return json.loads(urllib.request.urlopen(url).read().decode('utf-8'))    
    
    def update(self, subject, message):
        url = ('https://graph.facebook.com/{}?access_token={}'
               ).format(self.note_id, self.access_token)
        data = urllib.parse.urlencode({'message' : message,
                                       'subject' : subject}).encode('utf-8')
        urllib.request.urlopen(url, data)
                
    def run(self):
        self.active, seen = True, []
        while self.active:
            data = self.comment()
            if data['data']:
                comment = data['data'][0]
                if comment['id'] not in seen:
                    seen.append(comment['id'])
                    self.process(comment['text'])

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('access_token', help='facebook graph api access token')
    parser.add_argument('note_id', help='facebook note id')
    
    arguments = parser.parse_args()
    
    wikipedia_bot = WikipediaBot(arguments.access_token, arguments.note_id)
    wikipedia_bot.run()  