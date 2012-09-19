import json
import os
import subprocess
import math
from discoder.lib import command
from discoder.lib import parse

__author__ = 'jb'
__metaclass__ = type



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
    return subprocess.Popen(cmd, stdout=stdout, stderr=stderr).communicate()


class Transcoder:
    _probe = None

    def __init__(self, filename, flavors=(), outdir=None):
        self.filename = filename
        self.parts = []
        self.flavors = flavors
        if outdir:
            basename = os.path.basename(filename)
            name, ext = os.path.splitext(basename)
            self.out = os.path.join(outdir, name) + '{info}.{ext}'
        else:
            self.out = None

        self.files = {
            'orig': self.conv_original(convert=False),
            'video': None,
            'audio': None,
            'parts': dict.fromkeys(flavors),
            'final': None,
        }
        self.orig_ok = False

    def probe(self, **kw):
        if self._probe is None:
            name = self.files['orig'] or self.filename
            sout, _ = run(command.probe(name, **kw))
            if kw.get('json'):
                self._probe = json.loads(sout)
            else:
                self._probe = parse.probe(sout)
        return self._probe


    def conv_original(self, convert=True):
        output = None if not self.out else self.out.format('{0}', '{1}')
        cmd = command.conv_original(self.filename, 'libx264', 'aac')
        if convert:
            run(cmd)
            self.orig_ok = True
        self.files['orig'] = cmd[-1]
        return self.files['orig']

    def separate(self):
        output = None if not self.out else self.out.format('{0}', '.mp4')
        cmds = command.separate(self.files['orig'], output)
        for c in cmds:
            run(c)

    def split(self, max_num, min_time):
        output = None if not self.out else self.out.format('{0}', '{1}')

        duration = self.probe().stream[0].duration
        duration = int(math.ceil(float(duration)))
        chunks = command.calculate_chunks(duration, max_num, min_time)

        cmds = command.split(self.files['orig'], chunks, output)
        for c in cmds:
            run(c)

        self.parts = [c[-1] for c in cmds]
        return self.parts


    def join(self):
        if not self.parts:
            raise Exception('Nothing to join.')
        ext = 'm2ts'
        cmds = command.transform_mpg(self.parts, ext)
        fnames = [c[-1] for c in cmds]
        for c in cmds:
            run(c)

        return [c[-1] for c in cmds]
