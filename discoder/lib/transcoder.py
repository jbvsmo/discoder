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

    def __init__(self, filename, outdir=None):
        self.filename = filename
        if outdir:
            basename = os.path.basename(filename)
            name, ext = os.path.splitext(basename)
            self.out = os.path.join(outdir, name) + '{info}.{ext}'
        else:
            self.out = None

    @property
    def probe(self):
        if self._probe is None:
            sout, _ = run(command.probe(self.filename))
            self._probe = parse.probe(sout)
        return self._probe

    def split(self, max_num, min_time):
        output = None if not self.out else self.out.format('{0}', '{1}')

        duration = self.probe.stream[0].duration
        duration = int(math.ceil(float(duration)))
        chunks = command.calculate_chunks(duration, max_num, min_time)

        cmds = command.split(self.filename, chunks, output)
        for c in cmds:
            run(c)

        return [c[-1] for c in cmds]
