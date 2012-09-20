from __future__ import division

__author__ = 'jb'

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

def seek_frame(frame, fps, plus_one=False):
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
    ms = round((fraction + plus_one) * tpf)
    return seconds_to_time(seconds, int(ms))
