# coding: utf-8
from discoder.lib import Obj

__author__ = 'JB'


class Flavor(object):
    def __init__(self, name, bv=None, av=None, res=None, audio=True):
        self.name = name
        self.audio = audio
        self.bitrate = Obj(video=bv, audio=av)
        self.resolution = None if res is None else Obj(w=res[0], h=res[1])

    @classmethod
    def orig(cls, audio=True):
        return cls('orig', audio=audio)

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

