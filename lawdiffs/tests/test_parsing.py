from nose import tools as nt

from .base import TestBase
from ..miner.parser.ors import OrsHtmlParser

class ParseTester(TestBase):

    def test_get_expected_subs(self):
        html = self.get_content('ors_ch17.html')
        chapter_str = '17'
        text = self.html_to_text(html)

        expected_subs = ['17.065', '17.075', '17.085', '17.095', '17.990']

        parser = OrsHtmlParser()
        returned_subs, text = parser.get_expected_subs(chapter_str, text)
        print('returned_subs: {v}'.format(v=returned_subs))
        assert(len(returned_subs) > 100)

