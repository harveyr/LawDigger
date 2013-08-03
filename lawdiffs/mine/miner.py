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

    sources = [
        {
            'version': 2001,
            'crawl': [
                'http://www.leg.state.or.us/ors_archives/2001ORS/vol1.html'
            ],
            'crawl_link_pattern': re.compile(r'\d+\.html')
        },
        {
            'version': 2009,
            'crawl': [
                'http://www.leg.state.or.us/ors_archives/2009/vol1.html'
            ],
            'crawl_link_pattern': re.compile(r'\d+\.html')
        },
        {
            'version': 2011,
            'crawl': [
                'http://www.leg.state.or.us/ors/vol1.html'
            ],
            'crawl_link_pattern': re.compile(r'\d+\.html')
        }
    ]

    def __init__(self):
        super(OrLawParser, self).__init__()
        self.subsection_re = re.compile('(\d+\.\d+)')
        self.title_re = re.compile('\d+\.\d+\s([\w|\s|;|,]+\.)')

    def run(self):
        repos.wipe_and_init(self.law_code)
        model = data_laws.get_model(self.law_code)
        model.drop_collection()

        for source in self.sources:
            version = source['version']
            urls = self.scrape_urls(source)
            for i in range(min(1, len(urls))):
                url = urls[i]
                logger.debug('url: {v}'.format(v=url))
                self.create_laws_from_url(url, version)

            self.commit(version)

        # law = data_laws.fetch_law(self.law_code, '1.060')
        # print(law.text(2011, formatted=True))

        # law = data_laws.fetch_law(self.law_code, '1.195')
        # diff = repos.get_tag_diff(law, '2001', '2011')
        # print('diff: {v}'.format(v=diff))

    def scrape_urls(self, source_dict):
        urls = []
        for url in source_dict['crawl']:
            soup = BeautifulSoup(self.fetch_html(url))
            url_base = url[:url.rindex('/')] + '/'
            for link in soup.find_all(href=source_dict['crawl_link_pattern']):
                full_link = url_base + link.get('href')
                urls.append(full_link)
        return urls

    def create_laws_from_url(self, url, version):
        soup = self.fetch_soup(url)
        current_law = None
        text_buffer = ''
        for s in soup.stripped_strings:
            s = ' '.join(s.splitlines())
            subs_matches = self.subsection_re.match(s)
            if subs_matches:
                section = subs_matches.group(1)
                # if section == '1.192':
                #     logger.setLevel(logging.DEBUG)
                # else:
                #     logger.setLevel(logging.INFO)

                remainder = s[len(section):].strip()
                logger.debug('remainder: {v}'.format(v=remainder))
                if remainder.isupper():
                    # Should be a heading
                    continue

                current_law = data_laws.get_or_create_law(
                    subsection=section, law_code=self.law_code)
                current_law.set_version_title(version, remainder)
                text_buffer = remainder
            else:
                if not s.isupper():
                    text_buffer += ' ' + s
            if current_law:
                current_law.set_version_text(version, text_buffer)

mongoengine_connect()
p = OrLawParser()
p.run()
