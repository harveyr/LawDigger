import re
from bs4 import BeautifulSoup
import logging

from .base import LawImporter, ImportException
from ...data import law_codes
from ...data.access import ors as da_ors
from .. import util
from ..parser.ors import OrsPdfParser, OrsHtmlParser


logger = logging.getLogger(__name__)


class OrsImporter(LawImporter):

    law_code = law_codes.OREGON_REVISED_STATUTES

    sources = [
        {
            'version': 2007,
            'url': 'http://www.leg.state.or.us/ors_archives/2007/2007ORS.html',
            'crawl_func': 'begin_pdf_crawl',
            'link_patterns': [
                re.compile(r'\d+\.pdf')
            ],
        },
        {
            'version': 2011,
            'url': 'http://www.leg.state.or.us/ors/ors_info.html',
            'crawl_func': 'begin_html_crawl',
            'link_patterns': [
                re.compile(r'vol\d+.html'),
                re.compile(r'\d+\.html')
            ]
        }
    ]

    def __init__(self):
        super(OrsImporter, self).__init__()

        self.subsection_re = re.compile('(\d+\.\d+)')
        self.title_re = re.compile('\d+\.\d+\s([\w|\s|;|,]+\.)')

    def import_version(self, version):
        target_source = None
        for source in self.sources:
            if source['version'] == version:
                target_source = source
                break
        if not target_source:
            raise Exception('No target source found for version {}'.format(
                version))
        self.import_source(target_source)
        # self.commit(source['version'])

    def import_source(self, source_dict):
        crawl_func = getattr(self, source_dict['crawl_func'])
        crawl_func(source_dict)

    def begin_pdf_crawl(self, source_dict):
        parser = OrsPdfParser()
        version = source_dict['version']
        logger.info('Beginning ORS Version {}'.format(version))
        url = source_dict['url']
        self.current_url_base = self.url_base(url)

        html = self.fetch_html(url)
        hrefs = re.findall(r'href="(\d+[a-z]?\.pdf)"', html)

        # Debugging
        start_at = '459a'
        only_one = False
        should_import = not bool(start_at or only_one)

        for rel_pdf_href in hrefs:
            link_url = self.current_url_base + rel_pdf_href
            if not should_import:
                if start_at and start_at in rel_pdf_href:
                    should_import = True
                else:
                    # logger.debug('Skipping ' + link_url)
                    continue
            logger.info('Attempting {} ({})'.format(
                link_url, self.hashed_filename(link_url)))
            try:
                text = self.fetch_pdf_as_text(link_url)
                parser.create_laws(text, version)
            except ImportException:
                logger.error('HTTPError while fetching {}'.format(link_url))
                pass

            if only_one and should_import:
                return
        logger.info('Finished importing ORS Version {}'.format(version))

    def begin_html_crawl(self, source_dict):
        """Begin crawling html statutes"""
        url = source_dict['url']
        url_base = self.url_base(url)
        soup = BeautifulSoup(self.fetch_html(url))
        version = source_dict['version']
        volume_rex = re.compile(r'Volume (\w+),')

        link_pattern = source_dict['link_patterns'][0]
        next_link_pattern = source_dict['link_patterns'][1]

        for link in soup.find_all(href=link_pattern):
            link_text = util.soup_text(link)
            volume_hit = volume_rex.search(link_text)
            volume_str = volume_hit.group(1)
            volume = da_ors.get_or_create_volume(
                version=version, volume_str=volume_str)
            link_url = url_base + link.get('href')
            html = self.fetch_html(link_url)
            self.crawl_vol_page_html(
                html, url_base, volume, next_link_pattern)
            break

    def crawl_vol_page_html(self, html, url_base, volume, link_pattern):
        parser = OrsHtmlParser()
        soup = BeautifulSoup(html)
        chapter_rex = re.compile(r'Chapter (\w+)\b')
        only = '17'
        for link in soup.find_all(href=link_pattern):
            text = util.soup_text(link)
            chapter_str = chapter_rex.search(text).group(1)
            chapter = da_ors.get_or_create_chapter(volume, chapter_str)

            link_url = url_base + link.get('href')
            html = self.fetch_html(link_url)

            if only and chapter_str != only:
                continue

            parser.create_laws_from_html(html, chapter)
