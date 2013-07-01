from __future__ import division
import os
import math
from discoder import proc
from discoder.conv.flavor import Flavor
from discoder.lib import command, parse

__author__ = 'jb'
__metaclass__ = type

DEBUG = 1

class Transcoder:
    _probe = None

    def __init__(self, filename, flavors=(), original=True, outdir=None):
        self.filename = filename
        self.flavors = list(flavors)
        if original:
            self.flavors.append(Flavor.orig())
        self.outdir = outdir
        self.parts = []
        self.audio_parts = None
        if outdir:
            basename = os.path.basename(filename)
            name, ext = os.path.splitext(basename)
            self.out = os.path.join(outdir, name) + '{info}.{ext}'
        else:
            self.out = None

    def __repr__(self):
        return "<File {0!r}>".format(self.filename.replace('\\', '/'))

    def as_t(self, filename):
        """ Return a filename as a Transcoder object with the same
            flavors and output directory.

            It'll use the type of current `self` object to allow subclassing
        """
        return type(self)(filename, self.flavors, self.outdir)

    def probe(self, json=False, **kw):
        """ Get the `ffprobe` information in a dict-like object

        :param json: Use the `json` print format. Disabled by default
        :param kw: Other kw arguments to `command.probe` function
        :return: Parsed output in a dict
        """
        if self._probe is None or DEBUG >= 2:
            sout, _ = proc.run_local(command.probe(self.filename, json=json, **kw))
            if json:
                self._probe = json.loads(sout)
            else:
                self._probe = parse.probe(sout)
        return self._probe

    def conv_original(self, convert=True):
        output = None if not self.out else self.out.format('{0}', '{1}')
        cmd = command.convert(self.filename, {}, output=output, audio=False)
        if convert:
            proc.run_local(cmd)
        return self.as_t(cmd[-1])

    def separate(self):
        output = None if not self.out else self.out.format('{0}', '.m4a')
        cmd = command.separate(self.filename, output)
        proc.run_local(cmd)
        self.audio_parts = [cmd[-1] for i in range(len(self.flavors))]

    def split(self, max_num, min_time=0, frames=True, time_to_frames=False,
              threads=None, runner=proc.run_many):
        output = None if not self.out else self.out.format('{0}', '{1}')

        probe = self.probe()
        vprobe = probe.streams[0]

        if frames:
            fps = vprobe.r_frame_rate
            if '/' in fps:
                a, b = fps.split('/')
                fps = int(a) / int(b)
            else:
                fps = float(fps)
            try:
                duration = int(vprobe.nb_frames)
            except Exception:
                time_duration = float(probe.format.duration)
                duration = int(round(time_duration * fps))
        else:
            fps = None
            try:
                duration = float(vprobe.duration)
            except Exception:
                duration = float(probe.format.duration)
            duration = int(math.ceil(duration))

        base_cmds = command.split(duration, max_num, min_time, fps, time_to_frames)
        no_container = command.no_container()

        cmds = []
        all_names = []
        for part, base in enumerate(base_cmds):
            base['other'] += no_container
            cmd, names =  command.convert(self.filename, self.flavors, base, ext='h264',
                                          part=part, threads=threads, output=output, audio=False)
            cmds.append(cmd)
            all_names.append(names)

        if runner:
            runner(cmds)

        self.parts = zip(*all_names)
        return cmds

    def join(self, remove_files=True):
        if not self.parts:
            raise Exception('Nothing to join.')

        for part, audio in zip(self.parts, self.audio_parts):
            name = part[0]
            output, extra = name.rsplit('_', 1)
            output += '.mp4'

            proc.run_local(command.join(part, output, audio=audio))

            if remove_files:
                for f in part:
                    os.remove(f)

        if remove_files and self.audio_parts:
            os.remove(self.audio_parts[0])
