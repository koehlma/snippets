#!/usr/bin/env python
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

### documentation will maybe added later

from __future__ import division, print_function

import sys
import os.path
import random
import time

import gtk
import gobject

import gplayer

class Player(object):
    def __init__(self):
        self._load_gui()
        self._load_player()
        self._playlist = []
        self._current = 0
        self._seek_action = False
        gobject.timeout_add(500, self._query_position)
    
    def _load_gui(self):
        self._builder = gtk.Builder()
        self._builder.add_from_file(os.path.join(os.path.dirname(__file__), 'example.xml'))
        self._window = self._builder.get_object('window')
        self._window.connect('destroy', self._quit)
        self._action = self._builder.get_object('action')
        self._name = self._builder.get_object('name')
        self._progress = self._builder.get_object('progress')
        self._seek = self._builder.get_object('seek')
        self._seek.connect('change-value', self._seek_position)
        self._builder.get_object('toggle').connect('clicked', self._toggle)
        self._builder.get_object('previous').connect('clicked', self._previous)
        self._builder.get_object('next').connect('clicked', self._next)
        self._builder.get_object('volume').connect('value-changed', self._volume)
        self._window.show()
    
    def _load_player(self):
        self._player = gplayer.Player()
        self._player.connect('started', self._started)
        self._player.connect('finished', self._finished)
    
    def _quit(self, window):
        gtk.main_quit()
        
    def _started(self, player):
        self._action.set_from_stock(gtk.STOCK_MEDIA_PAUSE, gtk.ICON_SIZE_BUTTON)
   
    def _finished(self, player):
        self._current += 1
        self._play()
    
    def _toggle(self, button):
        if self._player.state == gplayer.STATE_PLAYING:
            self._player.pause()
            self._action.set_from_stock(gtk.STOCK_MEDIA_PLAY, gtk.ICON_SIZE_BUTTON)
        elif self._player.state == gplayer.STATE_PAUSED:
            self._player.play()
            self._action.set_from_stock(gtk.STOCK_MEDIA_PAUSE, gtk.ICON_SIZE_BUTTON)
    
    def _previous(self, button):
        self._player.stop()
        self._current -= 1
        self._play()
    
    def _next(self, button):
        self._player.stop()
        self._current += 1
        self._play()

    def _volume(self, button, value):
        self._player.volume = value
    
    def _seek_position(self, scale, type, value):
        nanoseconds = self._player.duration[3]
        self._seek_value = nanoseconds * (value / 100)
        self._seek_action = True
        self._seek_time = time.time()
    
    def _play(self):
        self._check_current()
        self._player.play_file(self._playlist[self._current])
        self._name.set_text(self._playlist[self._current])    
    
    def _check_current(self):
        if self._current < 0:
            self._current = len(self._playlist) - 1
        elif self._current > len(self._playlist) - 1:
            self._current = 0
    
    def _query_position(self):
        if self._player.state == gplayer.STATE_PLAYING:
            position = self._player.position
            duration = self._player.duration
            self._progress.set_text('%02i:%02i / %02i:%02i' % (position[0], position[1],
                                                               duration[0], duration[1]))
            self._progress.set_fraction(position[3] / duration[3])
            self._seek.set_value((position[3] / duration[3]) * 100)
        if self._seek_action:
            if time.time() - self._seek_time > 1:
                self._player.position = self._seek_value
                self._seek_action = None
        return True
    
    def generate_playlist(self, path):
        for dirpath, dirnames, filenames in os.walk(path):
            for filename in filenames:
                if filename.split('.').pop() == 'mp3':
                    self._playlist.append(os.path.join(dirpath, filename))
        random.shuffle(self._playlist)
        if self._playlist:
            return True
        return False
    
    def start(self):
        self._play()

if __name__ == '__main__':
    if not len(sys.argv) == 2:
        print('usage: %s directory' % (sys.argv[0]))
    elif not os.path.isdir(sys.argv[1]):
        print('please give a valid directory')
    else:
        gobject.threads_init()
        main = Player()
        if main.generate_playlist(sys.argv[1]):
            main.start()
            gtk.main()
        else:
            print('no mp3 files found in given directory')