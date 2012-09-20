from __future__ import division
import unittest
from discoder.lib import helper

__author__ = 'jb'

class HelperTest(unittest.TestCase):

    def test_seconds_to_time(self):
        s = helper.seconds_to_time
        self.assertEqual(s(10), '00:00:10.000')
        self.assertEqual(s(60), '00:01:00.000')
        self.assertEqual(s(65, 4), '00:01:05.004')
        self.assertEqual(s(3600), '01:00:00.000')
        self.assertEqual(s(3850), '01:04:10.000')
        self.assertEqual(s(3599, 29), '00:59:59.029')
        self.assertEqual(s(10, 5001), '00:00:15.001')

    def test_seek_frame(self):
        sf = helper.seek_frame
        st = helper.seconds_to_time
        self.assertEqual(sf(133, 25), '00:00:05.320')
        self.assertEqual(sf(30000, 30000/1001), st(1001)) # 29.97 fps
        self.assertEqual(sf(1, 10), '00:00:00.100')

    def test_calculate_chunks(self):
        cc = helper.calculate_chunks
        self.assertEqual(cc(10, 5, 3), [(0, 4), (4, 7), (7, None)])
        self.assertEqual(cc(10, 5, 12), [(0, None)])
        self.assertEqual(cc(3, 5, 0), [(0, 1), (1, 2), (2, None)])