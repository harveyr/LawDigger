import re
from bs4 import BeautifulSoup
import logging

from .. import util
from ..base import LawImporter
from ...data import law_codes
from ...data.access import ors as da_ors

logger = logging.getLogger(__name__)


class ImportException(Exception):
    pass


class OrsImporterBase(LawImporter):

    law_code = law_codes.OREGON_REVISED_STATUTES

    sources = [
        {
            'version': 2007,
            'url': 'http://www.leg.state.or.us/ors_archives/2007/2007ORS.html',
            'type': 'pdf',
            'link_patterns': [
                re.compile(r'\d+\.pdf')
            ],
        },
        {
            'version': 2011,
            'url': 'http://www.leg.state.or.us/ors/ors_info.html',
            'type': 'html',
            'link_patterns': [
                re.compile(r'vol\d+.html'),
                re.compile(r'\d+\.html')
            ]
        }
    ]

    def get_source_dict(self, version):
        target_source = None
        for source in self.sources:
            if source['version'] == version:
                target_source = source
                break
        if not target_source:
            raise Exception('No target source found for version {}'.format(
                version))
        return target_source

    def import_version_by_subsection(self, version):
        target_source = self.get_source_dict(version)
        self.import_source(target_source, True)

    def create_parser(self, source_type, by_subsection):
        raise NotImplementedError()

    def import_source(self, source_dict, by_subsection=True):
        source_type = source_dict['type']
        parser = self.create_parser(source_type, by_subsection)
        if source_type == 'html':
            self.begin_html_crawl(source_dict, parser)
        elif source_type == 'pdf':
            self.begin_pdf_crawl(source_dict, parser)
        else:
            raise Exception('Unhandled source type: {}'.format(source_type))

    def begin_pdf_crawl(self, source_dict, parser):
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

    def begin_html_crawl(self, source_dict, parser):
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
                html, url_base, volume, next_link_pattern, parser)

    def crawl_vol_page_html(self, html, url_base, volume, link_pattern, parser):
        soup = BeautifulSoup(html)
        chapter_rex = re.compile(r'Chapter (\w+)\b')

        start_at = '129'
        only_one = True
        do_it = not bool(start_at)

        for link in soup.find_all(href=link_pattern):
            text = util.soup_text(link)
            chapter_str = chapter_rex.search(text).group(1)

            if start_at and start_at == chapter_str:
                do_it = True
            if not do_it:
                continue

            chapter = da_ors.get_or_create_chapter(volume, chapter_str)

            link_url = url_base + link.get('href')
            html = self.fetch_html(link_url)

            text = util.html_to_text(html)
            parser.create_laws(text, chapter)

            if start_at and only_one and do_it:
                break
