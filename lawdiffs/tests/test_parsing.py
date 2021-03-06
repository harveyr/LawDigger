import re
from nose import tools as nt
from mock import Mock, patch

from .base import TestBase, MockDoc
from ..miner.ors.subsection import OrsHtmlSubsectionParser
from ..data import encoder


class ParseTester(TestBase):

    def test_get_expected_subs(self):
        html = self.get_content('ors_ch17.html')
        chapter_str = '17'
        text = self.html_to_text(html)

        expected_subs = ['17.065', '17.075', '17.085', '17.095', '17.990']

        parser = OrsHtmlSubsectionParser()
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

        rex = OrsHtmlSubsectionParser.end_of_sentence_rex
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

        rex = OrsHtmlSubsectionParser.end_of_sentence_rex
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

        parser = OrsHtmlSubsectionParser()
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

    def test_find_title_with_commas(self):
        text = self.get_content('ors_ch40_2011.html')
        expected_title = 'Execution, Formalities and Interpretation of Writings'

        parser = OrsHtmlSubsectionParser()
        found_title = parser.get_chapter_title('42', text)

        nt.assert_equal(
            expected_title,
            found_title)

    def test_ors_2011_ch_129(self):
        """This chapter has 'UPIA' after each section number. This breaks
        with the original heading regexes."""

        content_file = 'ors_ch129_2011.html'
        text = self.get_content(content_file)
        version = 2011
        chapter_str = '129'
        expected_body_start = "129.200\nUPIA\n101. Short title.\nThis chapter may"

        parser = OrsHtmlSubsectionParser()

        text = parser.preprocess_text(version, chapter_str, text)
        expected_subs, body_text = parser.get_expected_subs(chapter_str, text)
        self.assert_startswith(body_text, '129.200')
        # print('expected_subs: {v}'.format(v=exected_subs))
        # print(body_text[:500])

        body_text = parser.purified_body_text(body_text)

        self.assert_startswith(
            body_text,
            expected_body_start)

        expected_subs, body_text = parser.get_expected_subs(chapter_str, text)
        nt.assert_equal('129.200', expected_subs[0])
        parser.assert_expected_subs_exist(chapter_str, expected_subs, body_text)

    def test_ch_title_with_apostrophe(self):
        content_file = 'ors_ch251_2011.html'
        text = self.get_content(content_file)
        version_str = '2011'
        chapter_str = '251'

        parser = OrsHtmlSubsectionParser()
        parser.get_chapter_title(version_str, chapter_str, text)

    def test_ch_title_with_comma(self):
        content_file = 'ors_ch473_2011.html'
        text = self.get_content(content_file)
        version_str = '2011'
        chapter_str = '473'

        parser = OrsHtmlSubsectionParser()
        parser.get_chapter_title(version_str, chapter_str, text)
