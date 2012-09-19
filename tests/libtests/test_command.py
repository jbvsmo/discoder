__author__ = 'jb'

import unittest
from discoder.lib import command

# Check if there's no explicit call to `ffmpeg` or others
tool = 'test_tool_name'

class CommandTest(unittest.TestCase):

    def test_base_cmd(self):
        b = command.base_cmd
        self.assertEqual(b('A', 'B'), ['A', '-y', '-i', 'B'])
        self.assertEqual(b('A', 'B', False), ['A', '-i', 'B'])

    def test_probe(self):
        name = 'test.mp4'
        cmd = command.probe(name, tool=tool)

        self.assertEqual(cmd[:3], [tool, '-v', 'quiet'])
        self.assertIn('-show_format', cmd)
        self.assertIn('-show_streams', cmd)
        self.assertNotIn('-show_packets', cmd)
        self.assertEqual(cmd[-1], name)

    def test_calculate_chunks(self):
        cc = command.calculate_chunks
        self.assertEqual(cc(10, 5, 3), [(0, 4), (4, 7), (7, None)])
        self.assertEqual(cc(10, 5, 12), [(0, None)])
        self.assertEqual(cc(3, 5, 0), [(0, 1), (1, 2), (2, None)])

    @unittest.skip(NotImplemented)
    def test_split(self):
        pass

    def test_separate(self):
        cmd = command.separate('test.mp4', tool=tool)
        self.assertEqual(len(cmd), 1) #only the audio

        a, = cmd
        self.assertEqual(a[0], tool)
        #self.assertEqual(v[0], tool)

        self.assertEqual(a[-1], 'test_audio.m4a')
        #self.assertEqual(v[-1], 'test_video.mp4')

