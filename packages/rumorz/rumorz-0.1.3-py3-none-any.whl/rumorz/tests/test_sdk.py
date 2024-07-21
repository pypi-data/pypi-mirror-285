import unittest
from rumorz.client import RumorzClient

rumorz = RumorzClient(api_key="",
                      api_url='')


class TestRumorz(unittest.TestCase):

    def test_sdk(self):
        self.assertTrue(True)
