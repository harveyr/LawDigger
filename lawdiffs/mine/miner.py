import urllib2
import re
from bs4 import BeautifulSoup
import logging
import pickle
import md5
import os
import bs4
import tempfile

from pdfminer.pdfparser import PDFParser, PDFDocument, PDFNoOutlines
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LAParams, LTTextBox, LTTextLine, LTFigure, LTImage

from ..data.client import mongoengine_connect
from ..data.access import laws as data_laws
from . import repos

logger = logging.getLogger(__name__)

CACHE_PATH = os.path.join(os.path.split(__file__)[0], '.cache')
CACHE_PICKLE_PATH = os.path.join(CACHE_PATH, 'index.p')


class LawParser(object):

    newline_re = re.compile(r"(?<=[a-z])\r?\n")

    def url_base(self, url):
        try:
            return url[:url.rindex('/')] + '/'
        except ValueError, e:
            raise ValueError('Could not find right slash in url ' + str(url))

    def get_url_file_extension(self, url):
        filename, extension = os.path.splitext(url.split('/')[-1])
        if not extension:
            raise Exception("No file extension for url {}".format(url))
        return extension.lower()

    def hashed_filename(self, url, force_extension=None):
        hash_ = md5.new(url).hexdigest()
        if force_extension:
            extension = force_extension
        else:
            extension = self.get_url_file_extension(url)
        return hash_ + extension

    def cache_file_path_for_url(self, url, force_extension=None):
        return os.path.join(
            CACHE_PATH,
            self.hashed_filename(url, force_extension))

    def cache_url_contents(self, url, contents):
        hashed_filename = self.hashed_filename(url)
        path = os.path.join(CACHE_PATH, hashed_filename)
        with open(path, 'w') as f:
            f.write(contents)

    def cache_pdf_text(self, url, text):
        cache_file_path = self.cache_file_path_for_url(
            url, force_extension='.txt')
        logger.debug('writing cache_file_path: {v}'.format(v=cache_file_path))
        with open(cache_file_path, 'w') as f:
            f.write(text)

    def fetch_cached_pdf_text(self, url):
        cache_file_path = self.cache_file_path_for_url(
            url, force_extension='.txt')
        if os.path.exists(cache_file_path):
            with open(cache_file_path, 'r') as f:
                return f.read()

    def fetch_cached_url(self, url):
        hashed_filename = self.hashed_filename(url)
        path = os.path.join(CACHE_PATH, hashed_filename)
        if os.path.exists(path) and os.path.isfile(path):
            with open(path, 'r') as f:
                logger.info('Using cached {} ({})'.format(
                    url, hashed_filename))
                return f.read()
        else:
            return None

    def fetch_cached_pdf(self, url):
        hashed_filename = self.hashed_filename(url)
        path = os.path.join(CACHE_PATH, hashed_filename)
        if os.path.exists(path) and os.path.isfile(path):
            logger.info('Using cached {} ({})'.format(
                url, hashed_filename))
            with open(path, 'rb') as f:
                return f.read()

    def fetch_html(self, url):
        cached = self.fetch_cached_url(url)
        if cached:
            return cached

        logger.info('Fetching ' + url)
        response = urllib2.urlopen(url)
        html = response.read()
        html = html.decode('utf-8', 'ignore')
        self.cache_url_contents(url, html)

        return html

    def fetch_soup(self, url):
        return BeautifulSoup(self.fetch_html(url))

    def with_open_pdf(self, url, extraction_callback, text_callback):
        if self.get_url_file_extension(url) != '.pdf':
            raise Exception('Not a pdf: {}'.format(url))
        logger.setLevel(logging.DEBUG)
        path = self.cache_file_path_for_url(url)
        if os.path.exists(path) and os.path.isfile(path):
            logger.debug('Using cached ' + url)
            with open(path, 'rb') as f:
                extraction_callback(url, f, text_callback)
        else:
            logger.debug('Fetching fresh ' + url)
            path = self.cache_file_path_for_url(url)
            response = urllib2.urlopen(url)
            with open(path, 'wb') as f:
                f.write(response.read())
            with open(path, 'rb') as f:
                extraction_callback(url, f, text_callback)

    def extract_pdf_text(self, url, open_file, text_callback):
        """Extract pdf text from open file and cache it."""
        parser = PDFParser(open_file)
        doc = PDFDocument()
        parser.set_document(doc)
        doc.set_parser(parser)
        doc.initialize()
        if not doc.is_extractable:
            raise Exception('Doc not extractable')
        rsrcmgr = PDFResourceManager()
        laparams = LAParams()
        device = PDFPageAggregator(rsrcmgr, laparams=laparams)
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        text_buffer = ' '
        for i, page in enumerate(doc.get_pages()):
            interpreter.process_page(page)
            layout = device.get_result()
            for obj in layout:
                try:
                    text = obj.get_text().encode('utf-8').rstrip()
                    for line in text.splitlines():
                        line = line.strip()
                        line = self.pdf_text_pre_append_hook(line)
                        if text_buffer[-1] == '-':
                            text_buffer = text_buffer[:-1]
                        else:
                            text_buffer += ' '
                        text_buffer += line
                except AttributeError:
                    pass

            # if i > 10:
            #     logger.warn('breaking on page {}'.format(i))
            #     break

        text_buffer = re.sub(r'\s{2}', ' ', text_buffer)
        self.cache_pdf_text(url, text_buffer)
        text_callback(text_buffer)

    def pdf_text_pre_append_hook(self, text):
        # Override as necessary
        return text

    def fetch_pdf_text(self, url, callback):
        """Fetch pdf text from url"""
        cached = self.fetch_cached_pdf_text(url)
        if cached:
            callback(cached)
            return
        self.with_open_pdf(url, self.extract_pdf_text, callback)

    def get_soup_text(self, soup_elem):
        try:
            text = soup_elem.get_text(',,,', strip=True).decode('utf-8')
            text = self.newline_re.sub(" ", text)
            text = re.sub(r',,,', '\n', text)
            return text
        except AttributeError:
            if isinstance(soup_elem, bs4.element.NavigableString):
                return unicode(soup_elem)
            else:
                raise Exception('Unhandled type: ' + str(soup_elem))

    def commit(self, version):
        laws = data_laws.fetch_code_version(self.law_code, version)
        logger.info('Writing version {}...'.format(version))
        for l in laws:
            repos.write_file(l, version)
        logger.info('Committing version {}...'.format(version))
        repos.commit(self.law_code, version)


class OrLawParser(LawParser):

    law_code = 'ors'

    volume_pat_html = re.compile(r'ORS Volume (\d+),')
    chapter_pat_html = re.compile(r'ORS Chapter (\d+)')
    pdf_subsection_re = re.compile(r'\b(\d+\.\d+)\b')
    pdf_footer1_re = re.compile(
        r'Title \d+ Page \d+ \(\d+ Edition\) \d+\.\d+ [A-Z;\s]+')
    pdf_footer2_re = re.compile(
        r'Title \d+ Page \d+ \(\d+ Edition\) [A-Z;\s]+ \d+\.\d+\s')

    sources = [
        {
            'version': 2007,
            'url': 'http://www.leg.state.or.us/ors_archives/2007/2007ORS.html',
            'crawl_func': 'begin_pdf_crawl',
            'link_patterns': [
                re.compile(r'\d+\.pdf')
            ],
            'fixes': [(
                u'Fees imposed under ORS 21.112. c.823 \u00A725 (enacted in lieu of 8.172); 2003 c.518 \u00A711] im[2001'.encode('utf-8'),
                u'Fees imposed under ORS 21.112. [2001 c.823 \u00A725 (enacted in lieu of 8.172); 2003 c.518 \u00A711]'.encode('utf-8')
            ), (
                'representing and 8.690 Advising',
                '8.690 Advising and representing'
            )
            ]
        },
        {
            'version': 2011,
            'url': 'http://www.leg.state.or.us/ors/ors_info.html',
            'crawl_func': 'begin_crawl_html',
            'link_patterns': [
                re.compile(r'vol\d+.html'),
                re.compile(r'\d+\.html')
            ]
        }
    ]

    def __init__(self):
        super(OrLawParser, self).__init__()
        self.subsection_re = re.compile('(\d+\.\d+)')
        self.title_re = re.compile('\d+\.\d+\s([\w|\s|;|,]+\.)')

    def run(self):
        repos.wipe_and_init(self.law_code)
        model = data_laws.get_statute_model(self.law_code)
        model.drop_collection()
        model = data_laws.get_volume_model(self.law_code)
        model.drop_collection()
        model = data_laws.get_chapter_model(self.law_code)
        model.drop_collection()

        logger.setLevel(logging.DEBUG)
        self.begin_pdf_crawl(self.sources[0])
        # self.commit(source['version'])
        return

        for source in self.sources:
            crawl_func = getattr(self, source['crawl_func'])
            crawl_func(source)
            self.commit(source['version'])

    def pdf_text_pre_append_hook(self, text):
        return text

    def begin_pdf_crawl(self, source_dict):
        url = source_dict['url']
        self.current_url_base = self.url_base(url)
        soup = BeautifulSoup(self.fetch_html(url))
        for link in soup.find_all(href=source_dict['link_patterns'][0]):
            self.current_version = source_dict['version']
            self.current_fixes = source_dict['fixes']
            link_url = self.current_url_base + link.get('href')
            # if not '003.pdf' in link_url:
            #     continue
            self.fetch_pdf_text(link_url, self.create_laws_from_pdf_text)

    def create_law_from_pdf_text(self, text, subsection, next_subsection=None):
        logger.debug(
            'subsection: {}, next: {}'.format(subsection, next_subsection))

        if not re.match(r'{}'.format(subsection), text):
            raise Exception(
                'Text does not start with subsection {}'.format(
                    start_section))

        if not next_subsection:
            raise Exception("Handle me!")

        law = data_laws.get_or_create_statute(subsection, self.law_code)
        text = text[len(subsection):].lstrip()

        next_section_split = next_subsection.split('.')
        next_section_pat = r'([\.:\]] {}\.{} [A-Z|\[])'.format(
            next_section_split[0], next_section_split[1])
        next_section_hit = re.search(next_section_pat, text)
        if not next_section_hit:
            logger.error('next_section_pat: {v}'.format(v=next_section_pat))
            raise Exception(
                'Could not find next section {} with text: "{}..."'.format(
                    next_subsection, text[:6000]))

        this_section_end_index = next_section_hit.start() + 2

        subsection_text = text[:this_section_end_index].strip()
        # logger.debug('subsection_text: {v}'.format(v=subsection_text))
        if subsection_text.startswith('['):
            if not subsection_text.endswith(']'):
                raise Exception(
                    'Unmatched brackets: {}'.format(subsection_text))
            law.set_version_text(self.current_version, subsection_text)
        else:
            title_split = subsection_text.split('.', 1)
            law.set_version_title(self.current_version, title_split[0])
            law.set_version_text(self.current_version, title_split[1])
        remainder = text[this_section_end_index:]
        # logger.debug('returning remainder: {v}...'.format(
            # v=remainder[:200]))
        return (law, remainder)

    def expected_subsections_from_pdf_text(self, text, chapter):
        chapter_subs_re = re.compile(r'\b({}\.\d+)'.format(chapter))

        subsections = []
        for match in chapter_subs_re.finditer(text):
            s = match.group(1)
            if s not in subsections:
                subsections.append(s)
        subsections.sort(key=float)
        logger.debug('subsections: {v}'.format(v=subsections))
        logger.debug('subsections[0]: {v}'.format(v=subsections[0]))
        first_subsection_re = re.compile(r'{} \S+'.format(subsections[0]))
        hit = first_subsection_re.search(text)
        return subsections, hit.start()

    def create_laws_from_pdf_text(self, text):
        """Assume one, big, pre-extracted string."""
        text = self.pdf_footer1_re.sub('', text)
        text = self.pdf_footer2_re.sub('', text)

        chapter_hit = re.search(r'Chapter (\d+)', text)
        chapter = chapter_hit.group(1)

        if self.current_fixes:
            for fix in self.current_fixes:
                text = text.replace(fix[0], fix[1])

        upper_pattern = r'[A-Z]+[A-Z;,\-\s]+'
        title_or_upper_pattern = r'[A-Z]+[A-Za-z;,\-\s]+'
        heading_patterns = [
            r'{u}(?:\({tu}\))?\s+{ch}\.\d+'.format(
                u=upper_pattern, tu=title_or_upper_pattern, ch=chapter),
            r'(\({tu}\)\s+{ch}\.\d+)'.format(
                tu=title_or_upper_pattern, ch=chapter)
        ]

        heading_matches = re.findall(
            r'[A-Z]+[A-Z\s,\-]+(?:\([A-za-z\s]+\))?\s+\d+\.\d+', text)
        for pattern in heading_patterns:
            logger.debug('pattern: {v}'.format(v=pattern))
            for match in re.findall(pattern, text):
                if match.startswith('ORS'):
                    continue
                logger.debug('match: "{v}"'.format(v=match))
                sub_str = [s for s in re.split(r'(\d+\.\d+)', match) if s][1]
                text = text.replace(match, sub_str)

        # Create list of expected subsections
        # subs_hit = self.pdf_subsection_re.search(text)
        subsections, start_index = self.expected_subsections_from_pdf_text(
            text, chapter)
        text = text[start_index:]
        current_law = None
        for i in range(len(subsections) - 1):
            subsection = subsections[i]
            logger.debug('starting subsection: {v}'.format(v=subsection))
            if not re.match(r'{}'.format(subsection), text):
                exception_print_idx = min(600, len(text))
                raise Exception(
                    'Text does not match expected subsection {}: "{}"'.format(
                        subsection, text[:exception_print_idx]))
            if i == len(subsections) - 1:
                next_subsection = None
            else:
                next_subsection = subsections[i + 1]
            law, remainder_text = self.create_law_from_pdf_text(
                text, subsection, next_subsection)
            text = remainder_text

    def begin_crawl_html(self, source_dict):
        """Begin crawling html statutes"""
        url = source_dict['url']
        self.current_url_base = self.url_base(url)
        soup = BeautifulSoup(self.fetch_html(url))
        for link in soup.find_all(href=source_dict['link_patterns'][0]):
            text = self.get_soup_text(link)
            volume = self.volume_pat_html.search(text).group(1)
            self.current_volume = data_laws.get_or_create_volume(
                volume, self.law_code)
            link_url = self.current_url_base + link.get('href')
            html = self.fetch_html(link_url)
            self.crawl_vol_page_html(html, source_dict)
            break

    def crawl_vol_page_html(self, html, source_dict):
        soup = BeautifulSoup(html)
        link_pattern = source_dict['link_patterns'][1]
        for link in soup.find_all(href=link_pattern):
            text = self.get_soup_text(link)
            chapter = self.chapter_pat_html.search(text).group(1)
            self.current_chapter = data_laws.get_or_create_chapter(
                chapter, self.current_volume, self.law_code)
            self.current_volume.add_chapter(self.current_chapter)

            link_url = self.current_url_base + link.get('href')

            self.current_source = data_laws.get_or_create_web_source(
                link_url)
            source_label = 'ORS Chapter {}'.format(chapter)
            self.current_source.set_label(source_label)

            html = self.fetch_html(link_url)
            self.create_laws_from_html(html, source_dict)
            break

    def create_laws_from_html(self, html, source_dict):
        version = source_dict['version']
        soup = BeautifulSoup(html)
        current_law = None
        text_buffer = ''
        set_title = False
        logger.setLevel(logging.DEBUG)
        count = 0
        for s in soup.stripped_strings:
            s = ' '.join(s.splitlines())
            # count += 1
            # if count > 20:
            #     break
            if not self.current_chapter.has_title(version):
                if set_title:
                    self.current_chapter.set_version_title(version, s)
                    set_title = False
                else:
                    regex = re.compile(
                        r'{}\.'.format(self.current_chapter.chapter))
                    if regex.match(s):
                        # Set the title on the next pass
                        set_title = True
                continue

            subs_matches = self.subsection_re.match(s)
            if subs_matches:
                section = subs_matches.group(1)
                remainder = s[len(section):].strip()
                if remainder.isupper():
                    # Should be a heading
                    continue

                if remainder and remainder[0].isupper():
                    current_law = data_laws.get_or_create_statute(
                        subsection=section, law_code=self.law_code)
                    current_law.set_version_title(version, remainder)
                    current_law.set_source(version, self.current_source)
                    logger.debug('current_law: {v}'.format(v=current_law))
                    self.current_chapter.add_statute(current_law)
                    text_buffer = ''
                else:
                    # If first char of remainder is not upper, it's part of
                    # a note or something.
                    text_buffer += remainder
            else:
                if not s.isupper():
                    text_buffer += ' ' + s
            if current_law:
                current_law.set_version_text(version, text_buffer)

mongoengine_connect()
p = OrLawParser()
p.run()
