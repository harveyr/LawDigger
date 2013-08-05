import urllib2
import re
from bs4 import BeautifulSoup
import logging
import pickle
import md5
import os
import bs4

from ..data.client import mongoengine_connect
from ..data.access import laws as data_laws
from . import repos

logger = logging.getLogger(__name__)

CACHE_PATH = os.path.join(os.path.split(__file__)[0], '.cache')
CACHE_PICKLE_PATH = os.path.join(CACHE_PATH, 'index.p')


class LawParser(object):
    cache = {
        'html': {}
    }

    newline_re = re.compile(r"(?<=[a-z])\r?\n")

    def __init__(self):
        # self.cleanse_html_re = re.compile(r'{}'.format(u'\xa7'))
        if os.path.exists(CACHE_PICKLE_PATH):
            with open(CACHE_PICKLE_PATH, 'r') as f:
                self.cache = pickle.load(f)

    def url_base(self, url):
        try:
            return url[:url.rindex('/')] + '/'
        except ValueError, e:
            raise ValueError('Could not find right slash in url ' + str(url))

    def fetch_html(self, url):
        hashed_filename = md5.new(url).hexdigest()
        if url in self.cache['html']:
            with open(os.path.join(CACHE_PATH, hashed_filename), 'r') as f:
                logger.info('Using cached {} ({})'.format(
                    url, hashed_filename))
                return f.read()

        logger.info('Fetching ' + url)
        response = urllib2.urlopen(url)
        html = response.read()
        html = html.decode('utf-8', 'ignore')

        self.cache['html'][url] = hashed_filename
        with open(os.path.join(CACHE_PATH, hashed_filename), 'w') as f:
            f.write(html)
        with open(CACHE_PICKLE_PATH, 'w') as f:
            pickle.dump(self.cache, f)

        return html

    def fetch_soup(self, url):
        return BeautifulSoup(self.fetch_html(url))

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
        logger.info('Committing version {}'.format(version))
        laws = data_laws.fetch_by_code(self.law_code, version)
        repos.update(laws, self.law_code, version)


class OrLawParser(LawParser):

    law_code = 'ors'

    volume_pat_html = re.compile(r'ORS Volume (\d+),')
    chapter_pat_html = re.compile(r'ORS Chapter (\d+)')

    sources = [
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
    # sources = [
    #     {
    #         'version': 2001,
    #         'crawl': [
    #             'http://www.leg.state.or.us/ors_archives/2001ORS/vol1.html'
    #         ],
    #         'crawl_link_pattern': re.compile(r'\d+\.html')
    #     },
    #     {
    #         'version': 2009,
    #         'crawl': [
    #             'http://www.leg.state.or.us/ors_archives/2009/vol1.html'
    #         ],
    #         'crawl_link_pattern': re.compile(r'\d+\.html')
    #     },
    #     {
    #         'version': 2011,
    #         'crawl': [
    #             'http://www.leg.state.or.us/ors/vol1.html'
    #         ],
    #         'crawl_link_pattern': re.compile(r'\d+\.html')
    #     }
    # ]

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

        for source in self.sources:
            func = getattr(self, source['crawl_func'])
            func(source)
            # urls = self.scrape_urls(source)
            # for i in range(min(1, len(urls))):
            #     url = urls[i]
            #     logger.debug('url: {v}'.format(v=url))
            #     self.create_laws_from_url(url, version)

            # self.commit(version)

        # law = data_laws.fetch_law(self.law_code, '1.060')
        # print(law.text(2011, formatted=True))

        # law = data_laws.fetch_law(self.law_code, '1.195')
        # diff = repos.get_tag_diff(law, '2001', '2011')
        # print('diff: {v}'.format(v=diff))

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
            html = self.fetch_html(link_url)
            self.create_laws_from_html(html, source_dict)
            break

    def create_laws_from_html(self, html, source_dict):
        version = source_dict['version']
        soup = BeautifulSoup(html)
        current_law = None
        text_buffer = ''
        set_title = False

        count = 0
        for s in soup.stripped_strings:
            s = ' '.join(s.splitlines())
            count += 1
            if count > 20:
                break
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
                    logger.debug('current_law: {v}'.format(v=current_law))
                    self.current_chapter.add_statute
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
