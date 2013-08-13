import os
import unittest
from nose import tools as nt

from ..miner import util
from ..miner.parser.ors import OrsParserBase

from ..data import encoder

TEST_CONTENT_PATH = os.path.join(os.path.split(__file__)[0], 'content')


class TheNothing(object):
    pass


class TestBase(unittest.TestCase):

    def get_content(self, filename, as_text=True):
        path = os.path.join(TEST_CONTENT_PATH, filename)
        contents = None
        with open(path, 'r') as f:
            contents = f.read()
        if as_text and filename.endswith('.html'):
            return self.html_to_text(contents)
        else:
            return contents

    def html_to_text(self, html):
        return util.html_to_text(html)

    def get_text_start_at_sub(self, sub, text, start_at=None):
        if start_at:
            text = text[start_at:]
        parser = OrsParserBase()
        rex = parser.build_subsection_rex(sub)
        hit = rex.search(text)
        text = text[hit.start():]
        return text

    def curly_quote_wrap(self, text):
        return '{}{}{}'.format(
            encoder.unicode_char('curly_left_quote'),
            text,
            encoder.unicode_char('curly_right_quote'))

    def unicode_char(self, key):
        return encoder.unicode_char(key)

    def assert_startswith(self, text, expected_str):
        text_start = text[:len(expected_str)]
        nt.assert_equal(
            expected_str,
            text_start)
