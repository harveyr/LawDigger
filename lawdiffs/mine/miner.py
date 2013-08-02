import urllib2
import re
from bs4 import BeautifulSoup
import logging
import pickle
import md5
import os

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

    def __init__(self):

        # self.cleanse_html_re = re.compile(r'{}'.format(u'\xa7'))

        if os.path.exists(CACHE_PICKLE_PATH):
            with open(CACHE_PICKLE_PATH, 'r') as f:
                self.cache = pickle.load(f)

    def fetch_html(self, url):
        hashed_filename = md5.new(url).hexdigest()
        if url in self.cache['html']:
            with open(os.path.join(CACHE_PATH, hashed_filename), 'r') as f:
                logger.info('Using cached version of {} ({})'.format(
                    url, hashed_filename))
                return f.read()

        logger.info('Fetching fresh version of ' + url)
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
        text = soup_elem.get_text(' ', strip=True).decode('utf-8')
        return text

    def commit(self, version):
        logger.info('Committing version {}'.format(version))
        repos.update(self.laws, version, self.state_code)


class OrLawParser(LawParser):

    state_code = 'or'

    sources = [
        {
            'version': 2001,
            'crawl': [
                'http://www.leg.state.or.us/ors_archives/2001ORS/vol1.html'
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
        self.section_re = re.compile('(\d+\.\d+)\s(\S)')
        self.title_re = re.compile('\d+\.\d+\s([\w|\s|;|,]+\.)')
        self.laws = []

    def run(self):
        repos.wipe_and_init(self.state_code)

        for source in self.sources:
            version = source['version']
            urls = self.scrape_urls(source)
            for i in range(min(2, len(urls))):
                url = urls[i]
                logger.debug('url: {v}'.format(v=url))
                self.create_laws_from_url(url, version)

            self.commit(version)

        # diff = repos.get_tag_diff('7.110', '1995', '2009', self.state_code)

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

        starting_elem = soup.find('b').parent.previous_sibling
        current_law = None

        for elem in starting_elem.next_siblings:
            try:
                text = self.get_soup_text(elem)
            except AttributeError:
                text = unicode(elem)
            subs_matches = self.section_re.match(text)
            if subs_matches:
                section = subs_matches.group(1)

                current_law = data_laws.get_or_create_law(
                    subsection=section, state_code='or')
                current_law.init_version(version)

                title_matches = self.title_re.match(text)
                if title_matches:
                    title = title_matches.group(1)
                    law_text = text[title_matches.end():]
                    law_text = law_text.strip()
                else:
                    title = ''
                    law_text = text[subs_matches.end() - 1:]
                    law_text = ' '.join(law_text.splitlines())

                current_law.set_version_title(version, title)
                current_law.append_version_text(version, law_text)
                current_law.save()
                self.laws.append(current_law)
            else:
                if text.isupper():
                    continue
                if not current_law:
                    raise Exception('No current law to append to')
                current_law.append_version_text(version, '\n' + text)


mongoengine_connect()
p = OrLawParser()
p.run()
