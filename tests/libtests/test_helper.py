import unittest
from discoder.lib.helper import seconds_to_time

__author__ = 'jb'

class HelperTest(unittest.TestCase):

    def test_seconds_to_time(self):
        s = seconds_to_time
        self.assertEqual(s(10), '00:00:10.000')
        self.assertEqual(s(60), '00:01:00.000')
        self.assertEqual(s(65, 4), '00:01:05.004')
        self.assertEqual(s(3600), '01:00:00.000')
        self.assertEqual(s(3850), '01:04:10.000')
        self.assertEqual(s(3599, 29), '00:59:59.029')
        self.assertEqual(s(10, 5001), '00:00:15.001')