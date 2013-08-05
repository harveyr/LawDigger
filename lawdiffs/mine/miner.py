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
        text_buffer = ''
        for i, page in enumerate(doc.get_pages()):
            interpreter.process_page(page)
            layout = device.get_result()
            for obj in layout:
                try:
                    text_buffer += ' ' + obj.get_text().encode('utf-8').strip()
                except AttributeError:
                    pass
        self.cache_pdf_text(url, text_buffer)
        text_callback(text_buffer)
        # return text_callback(text_buffer.encode('utf-8'))

    def fetch_pdf_text(self, url, callback):
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

    sources = [
        {
            'version': 2007,
            'url': 'http://www.leg.state.or.us/ors_archives/2007/2007ORS.html',
            'crawl_func': 'begin_crawl_pdf',
            'link_patterns': [
                re.compile(r'\d+\.pdf')
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
        self.begin_crawl_pdf(self.sources[0])
        return

        for source in self.sources:
            crawl_func = getattr(self, source['crawl_func'])
            crawl_func(source)
            self.commit(source['version'])

        # law = data_laws.fetch_law(self.law_code, '1.060')
        # print(law.text(2011, formatted=True))

        # law = data_laws.fetch_law(self.law_code, '1.195')
        # diff = repos.get_tag_diff(law, '2001', '2011')
        # print('diff: {v}'.format(v=diff))

    def begin_crawl_pdf(self, source_dict):
        url = source_dict['url']
        self.current_url_base = self.url_base(url)
        soup = BeautifulSoup(self.fetch_html(url))
        for link in soup.find_all(href=source_dict['link_patterns'][0]):
            link_url = self.current_url_base + link.get('href')
            self.fetch_pdf_text(link_url, self.create_laws_from_pdf_text)
            break

    def create_laws_from_pdf_text(self, text):
        """Assume one, big, pre-extracted string."""
        first_subsection = None
        for line in text.splitlines():
            print(line)

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
