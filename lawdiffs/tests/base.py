import os
import unittest
from ..miner import util

TEST_CONTENT_PATH = os.path.join(os.path.split(__file__)[0], 'content')


class TestBase(unittest.TestCase):

    def hi(self):
        print('hi')

    def get_content(self, filename):
        path = os.path.join(TEST_CONTENT_PATH, filename)
        with open(path, 'r') as f:
            return f.read()

    def html_to_text(self, html):
        return util.html_to_text(html)
