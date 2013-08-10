import re
import logging
from ...data import law_codes
from ...data.access import laws as da_laws
logger = logging.getLogger(__name__)


class OrsPdfParser(object):
    law_code = law_codes.OREGON_REVISED_STATUTES

    volume_pat_html = re.compile(r'ORS Volume (\d+),')
    chapter_pat_html = re.compile(r'ORS Chapter (\d+)')
    pdf_subsection_re = re.compile(r'\b(\d+\.\d+)\b')
    pdf_footer1_re = re.compile(
        r'Title \d+ Page \d+ \(\d+ Edition\) \d+\.\d+ [A-Z;\s]+')
    pdf_footer2_re = re.compile(
        r'Title \d+ Page \d+ \(\d+ Edition\) [A-Z;\s]+ \d+\.\d+\s')

    upper_pat = r"[A-Z]+[A-Z;,'\-\s]+"
    title_or_upper_pat = r"[A-Z]+[A-Za-z;,'\-\s]+"
    dash_space_re = re.compile(r'\w\-\s\w')

    def chapter_subs_pattern(self, chapter):
        """Get basic chapter subsection pattern."""
        return '{}\.\d+'.format(chapter)

    def get_chapter_from_pdf_text(self, text):
        chapter_hit = re.search(r'Chapter (\d+)', text)
        chapter = chapter_hit.group(1)
        return chapter

    def pdf_text_has_laws(self, text, chapter):
        if re.search(
                r'^Chapter {}\s\(Former Provisions\)'.format(chapter),
                text):
            return False
        return True

    def find_expected_subs_in_pdf_text(self, text, chapter):
        ch_subs_pat = self.chapter_subs_pattern(chapter)

        first_subs_hit = re.search(
            r'^({})\s[A-Z]'.format(ch_subs_pat), text, re.MULTILINE)
        first_subs = first_subs_hit.group(1)
        first_subs_idx = first_subs_hit.end()

        search_text = text[first_subs_idx:]
        first_full_subs_hit = re.search(
            r'^({})\s[A-Z]'.format(first_subs),
            search_text,
            re.MULTILINE)

        first_full_subs_idx = first_full_subs_hit.start() + first_subs_idx

        # Find all TOC subsections
        search_text = text[:first_full_subs_idx]
        subsection_re = re.compile(
            r'^({})\s[A-Z]'.format(ch_subs_pat), re.MULTILINE)

        expected_subsections = subsection_re.findall(search_text)
        filtered = []
        for sub in expected_subsections:
            if sub not in filtered:
                filtered.append(sub)
        return (filtered, text[first_full_subs_idx:])

    def remove_margins_from_pdf_text(self, text, chapter):
        """Remove headers and footers."""
        heading_rexes = [
            re.compile(
                r'^Title \d+ Page \d+ \(\d+ Edition\)$',
                re.MULTILINE),
            re.compile(
                r'^{}\.\d+\s{}$'.format(chapter, self.upper_pat),
                re.MULTILINE),
            re.compile(
                r'^{}\s{}$'.format(
                    self.upper_pat,
                    self.chapter_subs_pattern(chapter)),
                re.MULTILINE),
            re.compile(
                r'^{}$'.format(self.upper_pat),
                re.MULTILINE)
        ]

        for rex in heading_rexes:
            if not rex.search(text):
                logger.warn(
                    'No heading found: Chapter {}, pattern {}'.format(
                        chapter, rex.pattern))
            else:
                text = rex.sub('', text)
        return text

    def create_laws_from_pdf_text(self, text, version):
        """Using this one for at least the 2007 pdf text."""

        chapter = self.get_chapter_from_pdf_text(text)
        if not self.pdf_text_has_laws(text, chapter):
            logger.warn('Skipping Chapter {} because it has no laws.'.format(
                chapter))
            return

        ch_subs_pat = self.chapter_subs_pattern(chapter)

        expected_subs, search_text = self.find_expected_subs_in_pdf_text(
            text, chapter)

        # Start searching the full statute definitions
        search_text = self.remove_margins_from_pdf_text(search_text, chapter)

        subsection_re = re.compile(
            r'^\s?({})\s[A-Z]'.format(ch_subs_pat), re.MULTILINE)
        full_subs = subsection_re.findall(search_text)
        if len(full_subs) != len(expected_subs):
            for sub in full_subs:
                if sub not in expected_subs:
                    logger.error('Unexpected: {}'.format(sub))
                if not sub:
                    logger.error('Bad sub: "{}"'.format(sub))
            for sub in expected_subs:
                if sub not in full_subs:
                    logger.error('Not found: {}'.format(sub))
                if not sub:
                    logger.error('Bad sub: "{}"'.format(sub))
            msg = 'Expected {} statutes in ch {}, found {}'.format(
                len(expected_subs), chapter, len(full_subs))
            raise Exception(msg)

        # text = text.decode('utf8')
        # prime_re = re.compile(u'\u2032\s?', re.UNICODE)
        # text = prime_re.sub("'", text)
        # text = text.encode('utf8')

        for i in range(len(expected_subs) - 1):
            target = expected_subs[i]
            logger.debug('Searching for ' + target)
            subs_hit = re.search(
                r'^\s?{}\s[A-Z]'.format(target), search_text, re.MULTILINE)
            if not subs_hit:
                raise Exception('{} not found in text:\n{}'.format(
                    target, search_text[:5000]))

            search_text = search_text[subs_hit.start() + len(target):].lstrip()
            parts = search_text.split('.')
            title = ' '.join(parts[0].splitlines())
            title = self.dash_space_re.sub('', title) + '.'
            logger.debug('title: {v}'.format(v=title))

            law_text = None
            search_text = '.'.join(parts[1:])
            if i < len(expected_subs) - 1:
                next_subsection = expected_subs[i + 1]
                next_subsection_hit = re.search(
                    r'^{}\s[A-Z]'.format(expected_subs[i + 1]),
                    search_text,
                    re.MULTILINE)
                if not next_subsection_hit:
                    raise Exception(
                        "Couldn't find {} after {} with text:\n{}".format(
                            next_subsection, target, search_text[:5000]))
                law_text = search_text[:next_subsection_hit.start()].strip()
            else:
                law_text = search_text.strip()
            if not law_text:
                raise Exception("Couldn't find law text for {}".format(target))

            law_text = ' '.join(law_text.splitlines())
            law_text = self.dash_space_re.sub('', law_text)

            law = da_laws.get_or_create_law(self.law_code, target)
            da_laws.set_law_version(law, version, title, law_text)
            if not version in law.versions:
                law.versions.append(version)
                law.save()
