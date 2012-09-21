# coding: utf-8
"""
    Create command line lists to run conversion and information tools
    Author: João Bernardo Oliveira
"""
from __future__ import division
import os.path
from discoder.lib import helper

__author__ = 'jb'
__metaclass__ = type

# Ability to seek before (fast) and after (accurate)
# the input stream on video conversions
FANCY_SEEK = False

conv_tool = 'ffmpeg'
info_tool = 'ffprobe'
av_extensions = 'm4a', 'mp4'
av_codec = 'aac', 'libx264'

def base_cmd(tool, filename, yes=True, pre=None):
    """ Basic command for transcoding tool (`ffmpeg` or `avconv`).
        Sets the filename and the yes information for preventing the
        program wait for the user to write "yes" or "no".

    :param tool: Transcoding tool. E.g. "ffmpeg"
    :type filename: str
    :type yes: bool
    :param pre: Commands to be added before the input element (-i)
    :return list<str>
    """
    cmd = [tool, '-y']
    if not yes:
        cmd.pop()
    if pre:
        cmd.extend(pre)
    cmd.extend(('-i', filename))
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

def split(length, max_num, min_time, fps=None, time_to_frames=False):
    """ Create a list of command lines to divide a video file into
        smaller chunks of aproximately same size. This command will
        also remove the audio track.

        generate the chunks from list of 2-tuples with start and stop times
        (in seconds) to realize cuts. The `stop` value may be None to go to
        the end of the video.

    :param length: The video length in seconds
    :type length: int
    :param max_num: The maximum amount of chunks that should be created.
    :type max_num: int
    :param min_time: The minimal amount of time/number of frames to create
           a video chunk.
    :param fps: If `length` is given in frames, this should be set to the
           video FPS value
    :param time_to_frames: If `min_time` is given in seconds and length is
           given in frames, this parameter should be True to convert
           the `min_time` to desired number of frames.
    :type min_time: int
    :return list<dict<str: data>> [{'-ss': ..., 'other': [...]}, ...]
    """
    if time_to_frames:
        min_time = helper.num_frames(min_time, fps)

    chunks = helper.calculate_chunks(length, max_num, min_time)

    base_opt = ['-an'] #Remove the audio at the convert pass
    cmd = []
    first = None
    for i, (start, stop) in enumerate(chunks):
        if fps:
            chunk = {'-ss': helper.seek_frame(start, fps)}
        else:
            chunk = {'-ss': helper.seconds_to_time(start)}
        if stop is not None:
            if fps:
                chunk['-vframes'] = str(stop - start)
            else:
                # -t is "time duration" and not "stop time"
                duration = helper.seconds_to_time(stop - start)
                chunk['-t'] = duration
        chunk['other'] = base_opt
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
    # No need to remove audio
    #cmds.append(base + ['-vcodec', 'copy', '-an', output.format('video', v)])

    return cmds

def convert(filename, flavor, base=None, vcodec=av_codec[1], acodec=av_codec[0],
            ext='mp4', output=None, tool=conv_tool):
    """ Generate commands to convert a video file based on a series of flavors.

    :param filename:
    :param base: Part of command with specific configurations to be added
           after the input element. E.g.: seek options, remove audio...
           E.g.: {'-x': 'y', ..., 'other': [...]}
           If FANCY_SEEK is true, the seek option should be added as a
           `key: value` element.
    :param output: The output filename with a positional formatting `{0}`
           element where the number of the chunk will be placed. If this
           parameter is None, the number will be placed before the extension
           of the filename: file.mp4 -> file_1.mp4, file_2.mp4 ...
    :param flavor: Dictionary with data to convert a video. All optional.
           {"name": flavor_name,
            "bitrate": (video_bitrate, audio_bitrate),
            "resolution": (width, height)}
    :return:
    """
    if base is None:
        base = {}
    pre = None
    post = base.pop('other', [])

    if FANCY_SEEK:
        ss = '-ss'
        seek = base.pop(ss, None)
        if seek:
            pre = [ss, seek]
            post.extend((ss, '0'))

    for i in base.iteritems():
        post.extend(i)

    cmd = base_cmd(tool, filename, pre=pre) + post + \
          ['-strict', 'experimental', '-flags', '+cgop',
           '-vcodec', vcodec, '-acodec', acodec]

    bitrate = flavor.get('bitrate')
    if bitrate:
        bv, ba = bitrate
        cmd.extend(('-b:v', bv, '-b:a', ba))
    else:
        cmd.append('-sameq')

    resolution = flavor.get('resolution')
    if resolution:
        cmd.extend(('-s', '{0}x{1}'.format(*resolution)))

    if output is None:
        name, ext_ = os.path.splitext(filename)
        output = name + '_{0}.{1}'

    cmd.append(output.format(flavor.get('name', 'orig'), ext))
    return cmd

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
