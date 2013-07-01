# coding: utf-8
"""
    Create command line lists to run conversion and information tools
    Author: João Bernardo Oliveira
"""
from __future__ import division
import os.path
from discoder.lib import helper
import sys

if sys.version_info >= (3, 0):
    basestring = str

__author__ = 'jb'
__metaclass__ = type

# Ability to seek before (fast) and after (accurate)
# the input stream on video conversions
FANCY_SEEK = False

conv_tool = 'ffmpeg'
info_tool = 'ffprobe'
av_extensions = 'm4a', 'mp4'
av_codec = 'libfdk_aac', 'libx264'

def base_cmd(tool, input, yes=True, pre=None):
    """ Basic command for transcoding tool (`ffmpeg` or `avconv`).
        Sets the filename and the yes information for preventing the
        program wait for the user to write "yes" or "no".

    :param tool: Transcoding tool. E.g. "ffmpeg"
    :param input: File name or other option (e.g. `concat`)
    :type yes: bool
    :param pre: Commands to be added before the input element (-i)
    :return list<str>
    """
    cmd = [tool, '-y']
    if not yes:
        cmd.pop()
    if pre:
        cmd.extend(pre)
    if isinstance(input, basestring):
        input = (input,)
    for i in input:
        cmd.extend(add_input(i))
    return cmd

def add_input(filename):
    """ Add other inputs to ffmpeg (e.g. audio)
    :param filename: Another input to ffmpeg
    :return: list<str>
    """
    return ['-i', filename]

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
    """ Creates a list of command lines to divide a video file into
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
        chunk['other'] = list(base_opt)
        cmd.append(chunk)
    return cmd

def separate(filename, output=None, ext=av_extensions[0], tool=conv_tool):
    """ Generates commands for separating mp4 file with only audio stream.

    :type filename: str
    :param output: The output filename with a positional formatting `{0}`
           element either "audio" or "video" will be placed. Also, a positional
           `{1}` element to add the extensions.
    :type output: str
    :param ext: Extentions for audio. AAC by default
    :type
    :param tool: Transcoding tool. E.g. "ffmpeg"
    :return list<list<str>>
    """

    if output is None:
        name, ext_ = os.path.splitext(filename)
        output = name + '_{0}.{1}'

    # Remove Video
    return base_cmd(tool, filename) + ['-acodec', 'copy', '-vn', output.format('audio', ext)]

    # Remove Audio
    # No need to remove audio
    #cmds.append(base + ['-vcodec', 'copy', '-an', output.format('video', v)])

def convert(filename, flavors, base=None, part=None, threads=None, vcodec=av_codec[1],
            acodec=av_codec[0], ext='mp4', output=None, audio=True, tool=conv_tool):
    """ Generates commands to convert a video file based on a series of flavors.

    :type filename: str
    :param flavors: List of `conv.flavor.Flavor` objects to convert a video
           into many flavors from a single decode.
    :param base: Part of command with specific configurations to be added
           after the input element. E.g.: seek options, remove audio...
           E.g.: {'-x': 'y', ..., 'other': [...]}
           If FANCY_SEEK is true, the seek option should be added as a
           `key: value` element.
    :param part: Number or other identifier for converting video parts.
    :param vcodec, acodec: Video and audio codecs (ffmpeg names)
    :param ext: Video extension for output.
    :param output: The output filename with a positional formatting `{0}`
           element where the number of the chunk will be placed. If this
           parameter is None, the number will be placed before the extension
           of the filename: file.mp4 -> file_A.mp4, file_B.mp4 ...
           A `{1}` element must be given to add an extension name.
           If `part` parameter is not None, a `{2}` element can be given to
           add the part value to avoid multiple file with the same name.
    :param tool: Transcoding tool. E.g. "ffmpeg"
    :return: list<str>
    """
    if base is None:
        base = {}
    pre = []
    post = base.pop('other', [])

    if FANCY_SEEK:
        ss = '-ss'
        seek = base.pop(ss, None)
        if seek:
            pre = [ss, seek]
            post.extend((ss, '0'))

    if threads:
        post.extend(('-threads', str(threads)))

    for i in base.iteritems():
        post.extend(i)

    cmd = base_cmd(tool, filename, pre=pre)
    repeat = post #+ ['-strict', 'experimental', '-flags', '+cgop']
    names = []

    for flavor in flavors:

        cmd.extend(repeat)

        if flavor.audio and audio:
            cmd.extend(('-acodec', acodec))
        else:
            cmd.append('-an')

        if flavor.video:
            cmd.extend(('-vcodec', vcodec))
        else:
            cmd.append('-vn')

        bitrate = flavor.bitrate
        if flavor.sameq:
            cmd.extend(['-crf', '23'])
        else:
            if flavor.video and bitrate.video:
                cmd.extend(('-b:v', bitrate.video))
            if flavor.audio and bitrate.audio:
                cmd.extend(('-b:a', bitrate.audio))

        if flavor.resolution:
            cmd.extend(('-s', '{0.w}x{0.h}'.format(flavor.resolution)))

        if output is None:
            name, ext_ = os.path.splitext(filename)
            if part is None:
                output = name + '_{0}.{1}'
            else:
                output = name + '_{0}_{2}.{1}'

        name = output.format(flavor.name, ext, part)
        cmd.append(name)
        names.append(name)

    return cmd, names

def join(filenames, output, base=(), audio=None, tool=conv_tool):
    """ Join the mpg files with cat

    :type filenames: list
    :param output: The final video file.
    :param base: Other commands to be added (e.g. add audio stream)
    :param tool: Transcoding tool. E.g. "ffmpeg"
    :return <list<str>>
    """
    filenames = 'concat:'  + format('|'.join(filenames))
    cmd = base_cmd(tool, filenames)
    if audio:
        cmd.extend(add_input(audio))

    cmd.extend(base)
    cmd.extend(('-vcodec', 'copy'))
    if audio:
        cmd.extend(('-acodec', 'copy'))

    cmd.append(output)
    return cmd

def no_container():
    """ Part of command to generate a container-free h.264 file
    :return: list<str>
    """
    return ['-bsf:v', 'h264_mp4toannexb']

def remove_container(filenames, ext='h264', tool=conv_tool):
    """ Transform mp4 files as raw h264 files to allow joining them with concat.

    :type filenames: list
    :param ext: `h264` extension
    :param tool: Transcoding tool. E.g. "ffmpeg"
    :return:list<list<str>>
    """
    _ = 'ffmpeg -i d_orig_0.mp4 -c copy o0.h264'
    base = ['-vcodec', 'copy'] + no_container()
    cmds = []
    for name in filenames:
        newname, ext_ = os.path.splitext(name)
        cmds.append(base_cmd(tool, name) + base + [newname + '.' + ext])
    return cmds
