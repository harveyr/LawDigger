import re
import logging
from ...data import law_codes
from ...data.access import laws as da_laws
from .base import ParseException

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

    def debug_missing_expected_sub(self, sub, text):
        self.log_header('debug_missing_expected_sub')
        logger.debug('Subsection:\t\t{}'.format(sub))

        logger.debug('Start of text:\t{}'.format(text[:30]))

        idx = text.index(sub)
        logger.debug('First instance at:\t{} ({})'.format(
            idx, text[idx:idx + 30]))

        # self.find_and_report(re.compile(r'{}'.format(sub)), text, True)

        re.compile('sub')
        # test_rex = re.compile(u'\u201C'.encode('utf8'))
        rex = re.compile(
            r'^\s?{}\s[A-Z{}]'.format(sub, u'\u201C'.encode('utf8')),
            re.MULTILINE)
        # pattern = sub + u' \u201C'.encode('utf8')
        # pattern = r'{}\s{}'.format(
        #     sub,
        #     u'\u201C'.encode('utf8'))
        test_result = rex.search(text)
        # test_result = re.search(pattern, text)
        logger.debug('test_result: {v}'.format(v=test_result))
        if test_result:
            logger.debug('test_result.start(): {v}'.format(v=test_result.start()))
        idx = text.index(u'\u201C'.encode('utf8'))
        logger.debug('idx: {v}'.format(v=idx))

    def debug_missing_body_sub(self, missing_sub, text, rex=None):
        self.log_header('debug_missing_body_sub')
        logger.debug('Missing:\t\t{}'.format(missing_sub))
        if rex:
            logger.debug('Pattern used:\t\t{}'.format(rex.pattern))

    def debug_toc_find_fail(self, text, attempted_rex=None):
        self.log_header('debug_toc_find_fail')
        logger.debug('Attempted pattern: {}'.format(attempted_rex.pattern))

    def debug_subs_find_fail(self, sub, text, attempted_rex):
        self.log_header('debug_subs_find_fail')
        logger.debug('Subsection:\t\t{}'.format(sub))
        logger.debug('Attempted pattern:\t{}'.format(attempted_rex.pattern))

        self.find_and_report(
            re.compile(r'{}'.format(sub)),
            text)

        self.find_and_report(
            re.compile(r'^\s?{}'.format(sub)),
            text)

        self.find_and_report(
            re.compile(r'{}.[A-Z]'.format(sub)),
            text)

        self.find_and_report(
            re.compile(ur'^\s?{}.{{1,2}}\u00A7'.format(sub),
                re.MULTILINE),
            text)

    def debug_heading_search(self, text):
        logger.setLevel(logging.DEBUG)
        rex = re.compile(r'^\([A-Z][a-z]+[^\.]', re.MULTILINE)
        result = rex.search(text)
        for match in rex.finditer(text):
            s = text[match.start():match.start() + 20]
            closing_paren = text.index(')', match.end())
            heading = text[match.start():closing_paren]
            if '.' in heading:
                continue
            logger.debug('heading: {v}'.format(v=heading))

    def debug_chapter_search(self, text, ch_found=None, rex=None):
        self.log_header('debug_chapter_search')
        if rex:
            logger.debug('Rex Used:\t\t{}'.format(rex.pattern))
        if ch_found:
            logger.debug('Chapter Found:\t{}'.format(ch_found))

        idx = text.index('Chapter')
        logger.debug('First instance ({}):\t{}'.format(
            idx, text[idx:idx + 15]))

        rex = re.compile(r'^Chapter (\w+)$', re.MULTILINE)
        hit = rex.search(text)
        logger.debug('hit.group(1): {v}'.format(v=hit.group(1)))
        logger.debug('text[hit.start():hit.end() + 5]: {v}'.format(v=text[hit.start():hit.end() + 5]))

debugger = OrsPdfDebugger()


class OrsPdfParser(object):
    """Using this one for at least the 2007 pdf text."""

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

    subs_title_start_pat = r'[A-Z{}]'.format(u'\u201C'.encode('utf8'))

    def chapter_subs_pattern(self, chapter):
        """Get basic chapter subsection pattern."""
        return '{}\.\d+'.format(chapter)

    def get_chapter(self, text):
        rex = re.compile(r'^Chapter (\w+)$', re.MULTILINE)
        chapter_hit = rex.search(text)
        if not chapter_hit:
            debugger.debug_chapter_search(text, rex=rex)
            raise ParseException('Failed to find chapter')
        chapter = chapter_hit.group(1)
        return chapter

    def pdf_text_has_laws(self, text, chapter):
        if re.search(
                r'^Chapter {}\s\(Former Provisions\)'.format(chapter),
                text):
            return False
        return True

    def find_expected_subs(self, text, chapter):
        ch_subs_pat = self.chapter_subs_pattern(chapter)

        first_sub_rex = re.compile(
            r'^({})\s{}'.format(ch_subs_pat, self.subs_title_start_pat),
            re.MULTILINE)
        first_subs_hit = first_sub_rex.search(text)

        if not first_subs_hit:
            debugger.debug_toc_find_fail(text, first_sub_rex)
            raise ParseException('Failed to find first subsection')

        first_subs = first_subs_hit.group(1)
        first_subs_idx = first_subs_hit.end()
        if first_subs_idx > 1000:
            raise ParseException('Unexpectedly high first subs index: {}'.format(
                first_subs_idx))

        search_text = text[first_subs_idx:]
        first_full_subs_rex = re.compile(
            r'^({})\s{}'.format(first_subs, self.subs_title_start_pat),
            re.MULTILINE)
        first_full_subs_hit = first_full_subs_rex.search(search_text)

        if not first_full_subs_hit:
            debugger.debug_subs_find_fail(
                first_subs, search_text, first_full_subs_rex)
            raise ParseException(
                'Failed finding first subs {} in text {}:'.format(
                    first_subs, search_text[:300]))

        first_full_subs_idx = first_full_subs_hit.start() + first_subs_idx

        # Find all TOC subsections
        search_text = text[:first_full_subs_idx]
        subsection_re = re.compile(
            r'^({})\s{}'.format(ch_subs_pat, self.subs_title_start_pat),
            re.MULTILINE)

        expected_subsections = subsection_re.findall(search_text)
        filtered = []
        for sub in expected_subsections:
            if sub not in filtered:
                filtered.append(sub)

        # Testing
        # if not '279C.650' in filtered:
        #     logger.setLevel(logging.DEBUG)
        #     logger.debug('filtered: {v}'.format(v=filtered))
        #     debugger.debug_missing_expected_sub('279C.650', search_text)
        #     raise Exception('nope')

        return (filtered, text[first_full_subs_idx:])

    def purify_text(self, text, chapter):
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
            re.compile(r'^{}$'.format(self.upper_pat), re.MULTILINE),
            re.compile(r'^\([A-Z][a-z]+?[^\.]\)', re.MULTILINE)
        ]

        for rex in heading_rexes:
            if not rex.search(text):
                logger.debug(
                    'No heading found: Chapter {}, pattern {}'.format(
                        chapter, rex.pattern))
            else:
                text = rex.sub('', text)

        # double_space_re = re.compile(r'\s\s')
        # while double_space_re.search(text):
        #     text = double_space_re.sub(' ', text)
        return text

    def find_full_subs(self, version, chapter, subsection, text):
        ch_subs_pat = self.chapter_subs_pattern(chapter)
        subsection_re = re.compile(
            r'^\s?({})\s[A-Z]'.format(ch_subs_pat), re.MULTILINE)
        full_subs = subsection_re.findall(search_text)

    def text_has_empty_subsection(self, subs, text):
        empty_subs_rex = re.compile(
            r'^\s?({})\s\['.format(subs), re.MULTILINE)
        return bool(empty_subs_rex.search(text))

    def assert_expected_subs_exist(self, chapter, expected_subs, text):
        ch_subs_pat = self.chapter_subs_pattern(chapter)

        full_subs_rex = re.compile(
            r'^\s?({})\s{}'.format(ch_subs_pat, self.subs_title_start_pat),
            re.MULTILINE)

        full_subs = set(full_subs_rex.findall(text))

        unexpected = [x for x in full_subs if x not in expected_subs]

        for sub in unexpected:
            if not self.text_has_empty_subsection(sub, text):
                logger.error('expected_subs: {v}'.format(v=expected_subs))
                raise ParseException(
                    'Unexpected subsection: {}'.format(sub))

        not_found = [x for x in expected_subs if x not in full_subs]
        if len(not_found) > 0:
            debugger.debug_missing_body_sub(not_found[0], text, full_subs_rex)
            raise ParseException('Subsections not found in body: {}'.format(
                not_found))

        return True

    def create_laws(self, text, version):

        chapter = self.get_chapter(text)

        if self.should_skip_for_now(version, chapter):
            logger.critical(
                'Purposely skipping entire chapter! ({} Ch. {})'.format(
                    version, chapter))
            return

        if not self.pdf_text_has_laws(text, chapter):
            logger.warn('Skipping Chapter {} because it has no laws.'.format(
                chapter))
            return

        # ch_subs_pat = self.chapter_subs_pattern(chapter)
        expected_subs, search_text = self.find_expected_subs(
            text, chapter)

        search_text = self.purify_text(search_text, chapter)

        self.assert_expected_subs_exist(chapter, expected_subs, search_text)

        # text = text.decode('utf8')
        # prime_re = re.compile(u'\u2032\s?', re.UNICODE)
        # text = prime_re.sub("'", text)
        # text = text.encode('utf8')

        for i in range(len(expected_subs) - 1):
            target = expected_subs[i]
            logger.debug('Searching for ' + target)
            subs_hit = re.search(
                r'^\s?{}\s{}'.format(target, self.subs_title_start_pat),
                search_text,
                re.MULTILINE)
            if not subs_hit:
                if self.text_has_empty_subsection(target, search_text):
                    logger.warn('HANDLE ME! Empty law')
                    continue

                exception_rex = self.subs_rex_exception(version, chapter, target)
                if exception_rex:
                    subs_hit = exception_rex.search(search_text)

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
                    r'^\s?{}\s{}'.format(next_subs, self.subs_title_start_pat),
                    re.MULTILINE)
                next_subs_hit = next_subs_rex.search(search_text)

                if not next_subs_hit:
                    rex = self.subs_rex_exception(version, chapter, next_subs)
                    if rex:
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
        if version == '2007':
            if chapter == '127':
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

    def should_skip_for_now(self, version, chapter):
        skippies = {
            '2007': {
                '259': True
            }
        }
        try:
            return skippies[version][chapter]
        except KeyError:
            return False

