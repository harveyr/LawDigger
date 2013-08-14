import os
import md5
import bs4
from bs4 import BeautifulSoup
import subprocess
import urllib2
import logging
import re


logger = logging.getLogger(__name__)


CACHE_PATH = os.path.join(os.path.split(__file__)[0], '.cache')
PDFBOX_BIN_PATH = os.path.join(
    os.path.split(__file__)[0],
    '../bin/pdfbox-app-1.8.2.jar')

if not os.path.exists(CACHE_PATH):
    raise Exception('Cache path does not exist: ' + CACHE_PATH)

if not os.path.exists(PDFBOX_BIN_PATH):
    raise Exception('PDFBox path does not exist: ' + PDFBOX_BIN_PATH)


def debug_unicode_exception(e, text):
    logger.setLevel(logging.DEBUG)
    position = int(re.search(r'in position (\d+)', str(e)).group(1))
    context = text[position - 20:position + 10]
    logger.debug('context: {v}'.format(v=context))

    # em_dash = re.search(ur'\u2014'.encode('utf8'), context)
    em_dash = re.search(r'{}'.format(u'\u2014'.encode('utf8')), context)
    if em_dash:
        logger.debug('Contains em dash')
    else:
        logger.debug('No em dash')

class ImportException(Exception):
    pass


class LawImporter(object):
    """Abstract."""

    def url_base(self, url):
        try:
            return url[:url.rindex('/')] + '/'
        except ValueError:
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
            logger.debug('Using cached {} ({})'.format(
                url, hashed_filename))
            with open(path, 'r') as f:
                return f.read()
        else:
            return None

    def fetch_html(self, url):
        cached = self.fetch_cached_url(url)
        if cached:
            logger.info('Using cached {} ({})'.format(
                url, self.hashed_filename(url)))
            return cached
        logger.info('Fetching ' + url)

        html = self.fetch_url_contents(url)
        # html = html.decode('utf8', 'ignore')
        # try:
        #     html = html.encode('utf8')
        # except UnicodeDecodeError as e:
        #     debug_unicode_exception(e, html)
        #     raise e
        self.cache_url_contents(url, html)

        return html

    def fetch_soup(self, url):
        return BeautifulSoup(self.fetch_html(url))

    def fetch_url_contents(self, url):
        try:
            response = urllib2.urlopen(url)
            return response.read()
        except urllib2.HTTPError as e:
            raise ImportException(
                'Failed to fetch {} ({})'.format(
                    url, e))

    def fetch_pdf_as_html(self, url):
        if not url.endswith('.pdf'):
            raise Exception('{} does not point to a pdf'.format(url))
        cached_html_path = self.cache_file_path_for_url(
            url, force_extension='.html')
        if os.path.exists(cached_html_path):
            logger.debug('Returning cached html for ' + url)
            with open(cached_html_path, 'r') as f:
                return f.read()

        cached_pdf_path = self.cache_file_path_for_url(url)
        if not os.path.exists(cached_html_path):
            logger.debug('Fetching fresh ' + url)
            contents = self.fetch_url_contents(url)
            with open(cached_pdf_path, 'wb') as f:
                f.write(contents)

        logger.debug('Converting pdf to html ({})'.format(url))
        cmd = ['java', '-jar', PDFBOX_BIN_PATH, 'ExtractText', '-html',
               cached_pdf_path, cached_html_path]

        returncode = subprocess.call(cmd)
        if returncode != 0:
            raise Exception('Bad returncode: {}'.format(returncode))

        with open(cached_html_path, 'r') as f:
            return f.read()

    def fetch_pdf_as_text(self, url):
        if not url.endswith('.pdf'):
            raise Exception('{} does not point to a pdf'.format(url))
        cached_text_path = self.cache_file_path_for_url(
            url, force_extension='.txt')
        if os.path.exists(cached_text_path):
            logger.debug('Returning cached text for {} ({})'.format(
                url, cached_text_path))
            with open(cached_text_path, 'r') as f:
                return f.read()

        cached_pdf_path = self.cache_file_path_for_url(url)
        if not os.path.exists(cached_pdf_path):
            logger.debug('Fetching fresh ' + url)
            url_contents = self.fetch_url_contents(url)
            with open(cached_pdf_path, 'w') as f:
                f.write(url_contents)

        logger.debug('Converting pdf to text ({})'.format(url))

        cmd = ['java', '-jar', PDFBOX_BIN_PATH, 'ExtractText', '-encoding', 'UTF-8',
               cached_pdf_path, cached_text_path]

        returncode = subprocess.call(cmd)
        if returncode != 0:
            raise Exception('Bad returncode: {}'.format(returncode))

        with open(cached_text_path, 'r') as f:
            return f.read()

    # def commit(self, version):
    #     laws = da_laws.fetch_code_version(self.law_code, version)
    #     logger.info('Writing version {}...'.format(version))
    #     for l in laws:
    #         repos.write_file(l, version)
    #     logger.info('Committing version {}...'.format(version))
    #     repos.commit(self.law_code, version)

    def do_nothing(self, *args):
        pass

