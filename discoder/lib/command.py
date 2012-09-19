# coding: utf-8
"""
    Create command line lists to run conversion and information tools
    Author: João Bernardo Oliveira
"""
from __future__ import division
import os.path
import itertools as it
from discoder.lib.helper import seconds_to_time

__author__ = 'jb'
__metaclass__ = type

conv_tool = 'ffmpeg'
info_tool = 'ffprobe'
av_extensions = ('m4a', 'mp4')

def base_cmd(tool, filename, yes=True):
    """ Basic command for transcoding tool (`ffmpeg` or `avconv`).
        Sets the filename and the yes information for preventing the
        program wait for the user to write "yes" or "no".

        :param tool: Transcoding tool. E.g. "ffmpeg"
        :type filename: str
        :type yes: bool
        :return list<str>
    """
    cmd = [tool, '-y', '-i', filename]
    if not yes:
        cmd.pop(1)
    return cmd

def probe(filename, format=True, streams=True, packets=False, json=False, tool=info_tool):
    """ Mount the command line for `ffprobe` or `avprobe`.
        The output can be parsed with `discoder.lib.parse.probe`.

        :type filename: str
        :param tool: Information tool. E.g. "ffprobe"
        :return list<str>
    """
    cmd = [tool, '-v', 'quiet']
    if json:
        cmd.extend(('-print_format', 'json'))
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

    base = base_cmd(tool, filename)
    base_opt = ['-vcodec', 'copy', '-acodec', 'copy']
    cmd = []
    for i, (start, stop) in enumerate(chunks):
        chunk = base + ['-ss', seconds_to_time(start)]
        if stop is not None:
            # -t is "time duration" and not "stop time"!
            duration = seconds_to_time(stop - start)
            chunk.extend(('-t', duration))
        chunk.extend(base_opt)
        chunk.append(output.format(i))
        cmd.append(chunk)
    return cmd

def separate(filename, output=None, exts=av_extensions, tool=conv_tool):
    """ Generate commands for separating mp4 file with only video stream
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
    base = base_cmd(tool, filename)
    cmds = []

    if output is None:
        name, ext = os.path.splitext(filename)
        output = name + '_{0}.{1}'

    # Remove Video
    cmds.append(base + ['-acodec', 'copy', '-vn', output.format('audio', a)])

    # Remove Audio
    cmds.append(base + ['-vcodec', 'copy', '-an', output.format('video', v)])

    return cmds

def conv_original(filename, vcodec, acodec, ext='mp4', output=None, tool=conv_tool):
    if output is None:
        name, ext_ = os.path.splitext(filename)
        output = name + '_{0}.{1}'

    return base_cmd(tool, filename) + ['-strict', 'experimental', '-sameq',
                                       '-vcodec', vcodec, '-acodec', acodec,
                                       output.format('orig', ext)]

def join_cat(filenames):
    """ Join the mpg files with cat

        :type filenames:list
        :return <list<str>>
    """
    return ['cat'] + filenames

def transform_mpg(filenames, ext='mpg', tool=conv_tool):
    """ Transform mp4 files as mpg to allow joining them with cat.

        :type filenames: list
        :param ext: `MPG` extension
        :param tool: Transcoding tool. E.g. "ffmpeg"
        :return:list<list<str>>
    """
    base = ['-vcodec', 'copy', '-acodec', 'copy']
    cmds = []
    for name in filenames:
        newname, ext_ = os.path.splitext(name)
        cmds.append(base_cmd(tool, name) + base + [newname + '.' + ext])
    return cmds

def transform_mp4(filename, ext=av_extensions[1], tool=conv_tool):
    """ Transforms a MPG file in MP4 without transcoding.

        :type filename: str
        :param ext: MP4 extension
        :param tool: Transcoding tool. E.g. "ffmpeg"
        :return list<str>
    """
    name, ext_ = os.path.splitext(filename)
    return base_cmd(tool, filename) + ['-vcodec', 'copy', '-acodec', 'copy', name + '.' + ext]
