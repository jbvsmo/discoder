import subprocess

__author__ = 'jb'

DEBUG = False
#DEBUG = True

def run_local(cmd, stdout=None, stderr=None, pipe=True):
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
        print(' '.join(cmd))
    return subprocess.Popen(cmd, stdout=stdout, stderr=stderr).communicate()

def run_many(cmds, stdout=None, stderr=None, pipe=True, run=run_local):
    """ Same as run but for more than one command. Might be replaced by
        a distributed approach.
    """
    for c in cmds:
        run(c, stdout, stderr, pipe)