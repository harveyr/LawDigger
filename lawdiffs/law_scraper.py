import urllib2
import re
import bs4
from bs4 import BeautifulSoup
import logging
import pickle
import md5
import os

from .data import models
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

    # def cleanse_html(self, html):
    #     return self.cleanse_html_re.sub('', html)
    #     # return html

    def fetch_soup(self, url):
        return BeautifulSoup(self.fetch_html(url))

    def get_soup_text(self, soup_elem):
        text = soup_elem.get_text(' ', strip=True).decode('utf-8')
        return text

    def commit(self, tag_name):
        repos.update(self.laws, tag_name, self.REPO_REL_PATH)


class OrLawParser(LawParser):

    REPO_REL_PATH = 'or'

    sources = [
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
        repos.wipe_and_init(self.REPO_REL_PATH)

        for source in self.sources:
            urls = self.scrape_urls(source)
            for i in range(min(2, len(urls))):
                url = urls[i]
                logger.debug('url: {v}'.format(v=url))
                self.create_laws_from_url(url, source['version'])

        # self.create_laws_from_url(
        #     'http://www.leg.state.or.us/ors_archives/1995ORS/007.html')

        # for law in self.laws:
        #     law.save()
        # self.commit('1995')

        # self.laws = []
        # self.create_laws_from_url(
        #     'http://www.leg.state.or.us/ors_archives/2009/007.html')
        # self.commit('2009')

        # diff = repos.get_tag_diff('7.110', '1995', '2009', self.REPO_REL_PATH)
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
                current_law = models.OregonRevisedStatute(section)
                logger.info('Created law: ' + str(current_law))
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
                self.laws.append(current_law)
            else:
                if text.isupper():
                    continue
                if not current_law:
                    raise Exception('No current law to append to')
                current_law.append_version_text(version, '\n' + text)


p = OrLawParser()
p.run()
