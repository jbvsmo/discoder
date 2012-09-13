# coding: utf-8
"""
    Create command line lists to run conversion and information tools
    Author: João Bernardo Oliveira
"""
from __future__ import division
import os.path
import itertools as it

__author__ = 'jb'
__metaclass__ = type

conv_tool = 'ffmpeg'
info_tool = 'ffprobe'
av_extensions = ('m4a', 'mp4')

def probe(filename, format=True, streams=True, packets=False, tool=info_tool):
    """ Mount the command line for `ffprobe` or `avprobe`.
        The output can be parsed with `discoder.lib.parse.probe`.

        :type filename: str
        :type tool: str
        :return: list
    """
    cmd = [tool, '-v', 'quiet']
    if format:
        cmd.append('-show_format')
    if streams:
        cmd.append('-show_streams')
    if packets:
        cmd.append('-show_packets')

    cmd.append(filename)
    return cmd


def calculate_chunks(length, max_num, min_time):
    """ Calculate the video chunks sizes in order to split a file in a
        certain amount of small files depending on its length and maximum number
        of transcoding boxes available.

        :param length: The video length in seconds
        :type length: int
        :param max_num: The maximum amount of chunks that should be created.
        :type max_num: int
        :param min_time: The minimal amount of time in seconds to create
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

def split(filename, chunks, output=None, tool=conv_tool):
    """ Create a list of command lines to divide a video file into
        smaller chunks of aproximately same size.

        :type filename: str
        :param output: The output filename with a positional formatting `{0}`
               element where the number of the chunk will be placed. If this
               parameter is None, the number will be placed before the extension
               of the filename: file.mp4 -> file_1.mp4, file_2.mp4 ...
        :type output: str
        :param chunks: List of 2-tuples with start and stop times (in seconds)
               to realize cuts. The `stop` value may be None to go to the end
               of the video.
        :param tool: Transcoding tool. E.g. "ffmpeg"
        :return list<list<str>>
    """
    if output is None:
        name, ext = os.path.splitext(filename)
        output = name + '_{0}' + ext

    base = [tool, '-i', filename, '-vcodec', 'copy', '-acodec', 'copy']
    cmd = []
    for i, (start, stop) in enumerate(chunks):
        chunk = base + ['-ss', str(start)]
        if stop:
            # -t is "time duration" and not "stop time"!
            chunk.extend(('-t', str(stop - start)))
        chunk.append(output.format(i))
        cmd.append(chunk)
    return cmd

def separate(filename, output=None, exts=av_extensions, tool=conv_tool):
    """
        Generate commands for separating mp4 file with only video stream
        and a m4a audio file.

        :type filename: str
        :param output: The output filename with a positional formatting `{0}`
               element either "audio" or "video" will be placed. Also, a positional
               `{1}` element to add the extensions.
        :type output: str
        :param exts: Extentions for audio and video files. AAC and MP4 by default
        :type
        :param tool: Transcoding tool. E.g. "ffmpeg"
        :return list<list<str>>
    """
    a, v = exts
    base = [tool, '-i', filename]
    cmds = []

    if output is None:
        name, ext = os.path.splitext(filename)
        output = name + '_{0}.{1}'

    # Remove Video
    cmds.append(base + ['-vn', output.format('audio', a)])

    # Remove Audio
    cmds.append(base + ['-an', output.format('video', v)])

    return cmds