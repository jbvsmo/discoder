# coding: utf-8
""" Copyright (c) 2013 João Bernardo Vianna Oliveira

    This file is part of Discoder.

    Discoder is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    Discoder is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with Discoder.  If not, see <http://www.gnu.org/licenses/>.
"""
from discoder.lib import Obj

__author__ = 'JB'


class Flavor(object):
    def __init__(self, name, bv=None, av=None, res=None, audio=True, video=True, sameq=False):
        self.name = name
        self.sameq = sameq
        self.audio = audio
        self.video = video
        self.bitrate = Obj(video=bv, audio=av)
        self.resolution = None if res is None else Obj(w=res[0], h=res[1])

    @classmethod
    def orig(cls):
        return cls('orig', sameq=True)

    def __repr__(self):
        opt = []
        if self.bitrate.video:
            opt.append('V={0.bitrate.video}bps'.format(self))
        if self.bitrate.audio:
            opt.append('A={0.bitrate.audio}bps'.format(self))
        if self.resolution:
            opt.append('{0.w}x{0.h}'.format(self.resolution))
        opt = ', '.join(opt)

        return 'Flavor<{0.name}{1}{2}>'.format(self, ': ' if opt else '', opt)

    def res(self):
        """ Resolution as a tuple or None
        :return:
        """
        #noinspection PyUnresolvedReferences
        return None if self.resolution else (self.resolution.w, self.resolution.h)

    def no_audio(self):
        """ New Flavor object without audio
        :return:
        """
        return Flavor(self.name, self.bitrate.video, None,
                      self.res(), False, self.video, self.sameq)

    def no_video(self):
        """ New Flavor object without video
        :return:
        """
        return Flavor(self.name, None, self.bitrate.audio,
                      self.res(), self.audio, False, self.sameq)

