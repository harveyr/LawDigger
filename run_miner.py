from lawdiffs.miner import repos
from lawdiffs.miner.importer.ors import OrsImporter
from lawdiffs.data import models
from lawdiffs.data.client import mongoengine_connect
from lawdiffs.data.access import laws as da_laws

mongoengine_connect()


ors_law_code = OrsImporter.law_code
repos.wipe_and_init(ors_law_code)
models.LawDivision.drop_collection()
models.LawVersion.drop_collection()

importer = OrsImporter()
importer.import_version(2011)
