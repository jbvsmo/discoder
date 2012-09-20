__author__ = 'jb'

def seconds_to_time(num, ms=0):
    """ Convert a number of seconds to time in the "hh:mm:ss.xxx" format
        where "xxx" is the number of milisseconds or zero if not given.
        :param num: Number of seconds.
        :type num: int
        :param ms: Milisseconds.
        :type ms: int
        :return str
    """
    ss, ms = divmod(ms, 1000)
    num += ss
    mm, ss = divmod(num, 60)
    hh, mm = divmod(mm, 60)
    return '{0:02}:{1:02}:{2:02}.{3:03}'.format(hh, mm, ss, ms)
