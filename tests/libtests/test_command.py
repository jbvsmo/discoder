__author__ = 'jb'

import unittest
from discoder.lib import command

class CommandTest(unittest.TestCase):

    def test_probe(self):
        name = 'test.mp4'
        tool = command.info_tool
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

