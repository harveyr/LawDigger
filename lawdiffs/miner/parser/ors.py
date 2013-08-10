import re
import logging
from ...data import law_codes
from ...data.access import laws as da_laws

logger = logging.getLogger(__name__)


class OrsPdfDebugger(object):

    def log_header(self, func_name):
        logger.setLevel(logging.DEBUG)
        logger.debug('--- OrsPdfDebugger.{} ---'.format(func_name))

    def log_completion(self):
        logger.debug('--- OrsPdfDebugger Finished ---')

    def log_hits(self, hits):
        for h in hits:
            logger.debug(' - Hit: {}'.format(h))

    def find_and_report(self, rex, text, log_hits=False):
        result_col = 50
        hits = rex.findall(text)
        count = str(len(hits))
        msg = '{} hits '.format(rex.pattern.encode('utf8'))

        dots = result_col - (len(msg) + len(count))
        if dots > 0:
            msg += ' '
            for i in range(dots - 1):
                msg += '.'
            msg += ' '
        msg += count
        logger.debug(msg)

        if log_hits:
            for hit in rex.finditer(text):
                logger.debug(' - Hit: {}'.format(
                    text[hit.start() - 20:hit.end() + 20]))

    def debug_find_sequence_fail(self, subs, next_subs, text, attempted_rex):
        self.log_header('debug_find_sequence_fail')
        logger.debug('Subsection:\t\t{}'.format(subs))
        logger.debug('Next Subsection:\t{}'.format(next_subs))
        logger.debug('Attempted pattern:\t{}'.format(attempted_rex.pattern))

        self.find_and_report(
            re.compile(r'{}'.format(next_subs)),
            text)

        self.find_and_report(
            re.compile(r'^\s?{}'.format(next_subs)),
            text)

        self.find_and_report(
            re.compile(r'{}.[A-Z]'.format(next_subs)),
            text)

        self.find_and_report(
            re.compile(ur'^\s?{}.{{1,2}}\u00A7'.format(next_subs),
                re.MULTILINE),
            text)


debugger = OrsPdfDebugger()


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
        chapter_hit = re.search(r'Chapter (\d+[A-Z]?)', text)
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

    def purify_pdf_text(self, text, chapter):
        """Remove headers, footers, double spaces, etc."""
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

        # double_space_re = re.compile(r'\s\s')
        # while double_space_re.search(text):
        #     text = double_space_re.sub(' ', text)
        return text

    def find_full_subs_in_pdf_text(self, version, chapter, subsection, text):
        ch_subs_pat = self.chapter_subs_pattern(chapter)
        subsection_re = re.compile(
            r'^\s?({})\s[A-Z]'.format(ch_subs_pat), re.MULTILINE)
        full_subs = subsection_re.findall(search_text)


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
        search_text = self.purify_pdf_text(search_text, chapter)

        subsection_re = re.compile(
            r'^\s?({})\s[A-Z]'.format(ch_subs_pat), re.MULTILINE)
        full_subs = subsection_re.findall(search_text)
        exception_rexes = {}
        if len(full_subs) != len(expected_subs):

            problems = []

            for sub in full_subs:
                if sub not in expected_subs:
                    problems.append(sub)
            for sub in expected_subs:
                if sub not in full_subs:
                    problems.append(sub)

            for sub in problems:
                rex = self.subs_rex_exception(version, chapter, sub)
                if not rex:
                    raise Exception('Problem subsection: {}'.format(sub))

                if not rex.search(search_text):
                    raise Exception('Exception rex failed for {}'.format(sub))

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
                exception_rex = self.subs_rex_exception(version, chapter, sub)
                logger.debug('exception_rex: {v}'.format(v=exception_rex))
                return
                if exception_rex:
                    subs_hit = exception_rex.search(search_text)
                    print('here')
                    return

            if not subs_hit:
                raise Exception('{} not found in text:\n{}'.format(
                    target, search_text[:500]))

            search_text = search_text[subs_hit.start() + len(target):].lstrip()
            parts = search_text.split('.')
            title = ' '.join(parts[0].splitlines())
            title = self.dash_space_re.sub('', title) + '.'
            logger.debug('title: {v}'.format(v=title))

            law_text = None
            search_text = '.'.join(parts[1:])
            if i < len(expected_subs) - 1:
                next_subs = expected_subs[i + 1]
                next_subs_rex = re.compile(
                    r'^\s?{}\s[A-Z]'.format(next_subs), re.MULTILINE)
                next_subs_hit = next_subs_rex.search(search_text)

                if not next_subs_hit:
                    rex = self.subs_rex_exception(version, chapter, next_subs)
                    next_subs_hit = rex.search(search_text)
                if not next_subs_hit:
                    raise Exception(
                        "Couldn't find {} after {}".format(
                            next_subs, target))
                law_text = search_text[:next_subs_hit.start()].strip()
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

    def subs_rex_exception(self, version, chapter, subsection):
        if int(version) == 2007:
            if int(chapter) == 127:
                if subsection in [
                        '127.800',
                        '127.805',
                        '127.810',
                        '127.815',
                        '127.820',
                        '127.825',
                        '127.830',
                        '127.835',
                        '127.840',
                        '127.845',
                        '127.850',
                        '127.855',
                        '127.860',
                        '127.865',
                        '127.870',
                        '127.875',
                        '127.880',
                        '127.885',
                        '127.890',
                        '127.895',
                        '127.897']:
                    return re.compile(
                        ur'^\s?%s.{1,2}\u00A7' % subsection,
                        re.UNICODE | re.MULTILINE)
