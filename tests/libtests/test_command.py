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
        self.assertEqual(b('A', 'B', pre=['C']), ['A', '-y', 'C', '-i', 'B'])
        self.assertEqual(b('A', 'B', False, pre=['C', 'D']),
                         ['A', 'C', 'D', '-i', 'B'])
        self.assertEqual(b('A', ['B','C'], False), ['A', '-i', 'B', '-i', 'C'])

    def test_probe(self):
        name = 'test.mp4'
        cmd = command.probe(name, tool=tool)

        self.assertEqual(cmd[:3], [tool, '-v', 'quiet'])
        self.assertIn('-show_format', cmd)
        self.assertIn('-show_streams', cmd)
        self.assertNotIn('-show_packets', cmd)
        self.assertEqual(cmd[-1], name)

    @unittest.skip(NotImplemented)
    def test_split(self):
        pass

    def test_separate(self):
        cmd = command.separate('test.mp4', tool=tool)

        self.assertEqual(cmd[0], tool)
        self.assertEqual(cmd[-1], 'test_audio.m4a')

