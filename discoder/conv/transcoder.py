from __future__ import division
import os
import subprocess
import math
from discoder.conv.flavor import Flavor
from discoder.lib import command, parse

__author__ = 'jb'
__metaclass__ = type

DEBUG = True

def run(cmd, stdout=None, stderr=None, pipe=True):
    """ Run a command in a list of arguments with Popen.
        returns the stdout and stderr outputs.

        :param cmd:
        :param stdout:
        :param stderr:
        :param pipe:
        :return:
    """
    if pipe:
        if stdout is None:
            stdout = subprocess.PIPE
        if stderr is None:
            stderr = subprocess.PIPE
    if DEBUG:
        print(cmd)
    return subprocess.Popen(cmd, stdout=stdout, stderr=stderr).communicate()

def run_many(cmds, stdout=None, stderr=None, pipe=True):
    """ Same as run but for more than one command. Might be replaced by
        a distributed approach.
    """
    for c in cmds:
        run(c, stdout, stderr, pipe)

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
        if self._probe is None or DEBUG:
            sout, _ = run(command.probe(self.filename, json=json, **kw))
            if json:
                self._probe = json.loads(sout)
            else:
                self._probe = parse.probe(sout)
        return self._probe

    def conv_original(self, convert=True):
        output = None if not self.out else self.out.format('{0}', '{1}')
        cmd = command.convert(self.filename, {}, output=output)
        if convert:
            run(cmd)
        return self.as_t(cmd[-1])

    def separate(self):
        output = None if not self.out else self.out.format('{0}', '.mp4')
        cmds = command.separate(self.filename, output)
        run_many(cmds)

    def split(self, max_num, min_time, frames=False, time_to_frames=False):
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
            duration = int(math.ceil(float(vprobe.duration)))

        base_cmds = command.split(duration, max_num, min_time, fps, time_to_frames)
        no_container = command.no_container()

        cmds = []
        all_names = []
        for part, base in enumerate(base_cmds):
            base['other'] += no_container
            cmd, names =  command.convert(self.filename, self.flavors, base,
                                          ext='h264', part=part, output=output)
            cmds.append(cmd)
            all_names.append(names)

        run_many(cmds)

        self.parts = zip(*all_names)
        return [[self.as_t(name) for name in part] for part in self.parts]

    def join(self, remove_files=True):
        if not self.parts:
            raise Exception('Nothing to join.')

        for part in self.parts:
            name = part[0]
            output, extra = name.rsplit('_', 1)
            output += '.mp4'

            run(command.join(part, output))

            if remove_files:
                for f in part:
                    os.remove(f)
