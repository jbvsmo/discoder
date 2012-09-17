__author__ = 'jb'

def seconds_to_time(num, fff=0):
    """ Convert a number of seconds to time in the "hh:mm:ss.fff" format
        where "fff" is the frame value and is zero if not given.
        :param num: Number of seconds.
        :type num: int
        :param fff: Number of frames.
        :type fff: int
        :return str
    """
    mm, ss = divmod(num, 60)
    hh, mm = divmod(mm, 60)
    return '{0:02}:{1:02}:{2:02}.{3:03}'.format(hh, mm, ss, fff)
