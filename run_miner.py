from lawdiffs.miner import repos
from lawdiffs.miner.ors.subsection import OrsSubsectionImporter
from lawdiffs.data import models
from lawdiffs.data.client import mongoengine_connect


mongoengine_connect()

importer = OrsSubsectionImporter()

ors_law_code = importer.law_code
repos.wipe_and_init(ors_law_code)
models.LawDivision.drop_collection()
models.LawVersion.drop_collection()

importer.import_version_by_subsection(2011)

