from lawdiffs.miner import repos, util
from lawdiffs.miner.importer.ors import OrsImporter
from lawdiffs.miner.parser.ors import OrsHtmlParser
from lawdiffs.data import models
from lawdiffs.data.client import mongoengine_connect
from lawdiffs.data.access import laws as da_laws
from bs4 import BeautifulSoup


mongoengine_connect()


ors_law_code = OrsImporter.law_code
repos.wipe_and_init(ors_law_code)
models.LawDivision.drop_collection()
models.LawVersion.drop_collection()

importer = OrsImporter()
importer.import_version(2011)

# parser = OrsHtmlParser()
# html = importer.fetch_html('http://www.leg.state.or.us/ors/017.html')
# soup = BeautifulSoup(html)
# text = util.soup_text(soup)
# print(text[1000:5000])
# subs, text = parser.get_expected_subs(text, '17')
# print('subs: {v}'.format(v=subs))
