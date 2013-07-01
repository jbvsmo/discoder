from __future__ import division
import itertools as it

__author__ = 'jb'


def star(fn):
    """ Decorate a function to receive a single argument and expand
        to multiple arguments. This is specially useful for mapping
        functions that can only send a single argmument. E.g.:
        `multiprocessing.Pool.map`.

    :param fn: Function to be decorated
    """
    def _star_args_fn(args):
        return fn(*args)
    return _star_args_fn

def seconds_to_time(num, ms=0):
    """ Convert a number of seconds to time in the "hh:mm:ss.xxx" format
        where "xxx" is the number of milliseconds or zero if not given.

    :param num: Number of seconds.
    :type num: int
    :param ms: Milliseconds.
    :type ms: int
    :return str
    """
    ss, ms = divmod(ms, 1000)
    num += ss
    mm, ss = divmod(num, 60)
    hh, mm = divmod(mm, 60)
    data = map(int, (hh, mm, ss, ms))
    return '{0:02}:{1:02}:{2:02}.{3:03}'.format(*data)

def seek_frame(frame, fps, plus_one=False, raw=False):
    """ Find the seek position with second and millissecond values
        based on video framerate and amount of frames to seek.

        From: http://superuser.com/a/459488/115185

    :param frame: frame number to seek
    :param fps: Video FPS value
    :param plus_one: Add one frame to deal with open or closed intervals
    :return: tuple<2, int>: (seconds, milliseconds)
    """
    seconds, fraction = divmod(frame, fps)
    tpf = 1000/fps # time per frame
    ms = int(round((fraction + plus_one) * tpf))

    if raw:
        return seconds, ms
    return seconds_to_time(seconds, ms)

def num_frames(time, fps):
    """ Find the amount of frames after a specified time.

    :param time: Number of seconds
    :param fps: Video FPS value
    :return: int
    """
    return int(time * fps)

def calculate_chunks(length, max_num, min_time):
    """ Calculate the video chunks sizes in order to split a file in a
        certain amount of small files depending on its length and maximum number
        of transcoding boxes available.

    :param length: The video length in seconds
    :type length: int
    :param max_num: The maximum amount of chunks that should be created.
    :type max_num: int
    :param min_time: The minimal amount of time/number of frames to create
           a video chunk.
    :type min_time: int
    :return: list<tuple<int, 2>>
    """
    if length < max_num * min_time:
        # min_time is limiting
        parts = length // min_time
    else:
        # max_num is limiting
        parts = max_num

    if parts:
        size, extra = divmod(length, parts)
    else:
        size, extra = length, 0

    # Add one extra second for each part until there's no more remainder.
    extras = it.chain(it.repeat(1, extra), it.repeat(0))
    i = 0
    elements = []
    while i < length:
        e = next(extras)
        elements.append((i, i + size + e))
        i += size + e

    # The last element has to be None to avoid cutting fractions of seconds.
    elements[-1] = elements[-1][0], None
    return elements
