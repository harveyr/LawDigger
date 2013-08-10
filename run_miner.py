from lawdiffs.mine import repos
from lawdiffs.mine.importer import OrsImporter
from lawdiffs.data.client import mongoengine_connect
from lawdiffs.data.access import laws as da_laws

mongoengine_connect()


ors_law_code = OrsImporter.law_code
repos.wipe_and_init(ors_law_code)
model = da_laws.get_statute_model(ors_law_code)
model.drop_collection()
model = da_laws.get_volume_model(ors_law_code)
model.drop_collection()
model = da_laws.get_chapter_model(ors_law_code)
model.drop_collection()

importer = OrsImporter()
importer.import_version(2007)
