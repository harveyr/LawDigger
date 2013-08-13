import re
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

    def test_end_of_sentence_rex_with_typical_case(self):
        target = '1.001'
        text = self.get_content('ors_ch1.html')
        text = self.get_text_start_at_sub(target, text, 5000)
        expected_title = 'State policy for courts.'
        expected_start_of_law = 'The Legislative Assembly hereby declares that,'

        sub_and_title = text[:text.index('.', 10) + 1]
        nt.assert_equal(
            '{} {}'.format(target, expected_title),
            sub_and_title)

        print('text[:200]: {v}'.format(v=text[:200]))

        rex = OrsHtmlParser.end_of_sentence_rex
        hit = rex.search(text)
        nt.assert_true(hit)
        law_text = text[hit.end():].strip()
        self.assert_startswith(law_text, expected_start_of_law)

    def test_end_of_sentence_rex_with_end_quote(self):
        target = '30.932'
        text = self.get_content('ors_ch30.html')
        text = self.get_text_start_at_sub(target, text, 50000)
        expected_start_of_law = 'As used in ORS 30.930 to 30.947,'

        # print('text[:100]: {v}'.format(v=text[:100]))

        rex = OrsHtmlParser.end_of_sentence_rex
        hit = rex.search(text)
        # hit_str = text[hit.start():hit.end()]
        nt.assert_true(hit)
        law_text = text[hit.end():].strip()
        self.assert_startswith(law_text, expected_start_of_law)

    def test_parse_ors_ends_with_quote(self):
        target = '30.932'
        next = '30.933'
        text = self.get_content('ors_ch30.html')
        text = self.get_text_start_at_sub(target, text, 50000)

        expected_title = "Definition of {} or {}".format(
            self.curly_quote_wrap('nuisance'),
            self.curly_quote_wrap('trespass.'))
        expected_start = '{} {}'.format(target, expected_title)
        expected_end = '[1993 c.792 {sec}33; 1995 c.703 {sec}2]'.format(
            sec=self.unicode_char('section'))

        parser = OrsHtmlParser()
        nt.assert_equal(expected_start, text[:len(expected_start)])

        law_dict, remainder = parser.parse_law(target, next, text)
        nt.assert_equal(
            expected_title,
            law_dict['title'])

        law_text = law_dict['text']
        end_of_text = law_text[-1 * len(expected_end):]
        # print('law_text[-50:]: {v}'.format(v=law_text[-50:]))
        nt.assert_equal(
            expected_end,
            end_of_text)
