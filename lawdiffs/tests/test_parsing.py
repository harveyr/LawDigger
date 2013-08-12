from nose import tools as nt
from mock import Mock

from .base import TestBase, TheNothing
from ..miner.parser.ors import OrsHtmlParser


class ParseTester(TestBase):

    def test_get_expected_subs(self):
        html = self.get_content('ors_ch17.html')
        chapter_str = '17'
        text = self.html_to_text(html)

        expected_subs = ['17.065', '17.075', '17.085', '17.095', '17.990']

        parser = OrsHtmlParser()
        returned_subs, text = parser.get_expected_subs(chapter_str, text)

        nt.assert_equal(
            len(expected_subs),
            len(returned_subs),
            "Length of returned subs does not match expected")

    def test_end_of_sentence_rex(self):
        text = self.get_content('ors_ch30.html')
        target = '30.932'
        expected_start_of_law = 'As used in ORS 30.930 to 30.947,'
        parser = OrsHtmlParser()
        rex = parser.build_subsection_rex(target)
        hit = rex.search(text[20000:])
        text = text[hit.start():]

        rex = parser.end_of_sentence_rex
        search = rex.search(text)
        nt.assert_true(search)
        law_text = text[search.start():]
        nt.assert_true(
            law_text[:len(expected_start_of_law)],
            expected_start_of_law)

    def test_parse_ors_ends_with_quote(self):
        target = '30.932'
        next = '30.933'
        text = self.get_content('ors_ch30.html')
        text = self.get_text_start_at_sub(target, text, 50000)

        expected_title = "Definition of {} or {}".format(
            self.curly_quote_wrap('nuisance'),
            self.curly_quote_wrap('trespass.'))
        expected_start = '{} {}'.format(target, expected_title)

        parser = OrsHtmlParser()
        nt.assert_equal(expected_start, text[:len(expected_start)])

        law_dict, remainder = parser.parse_law(target, next, text)
        nt.assert_equal(
            law_dict['title'],
            expected_title)

