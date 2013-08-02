# import mongoengine as moe
from .. import models
import logging

logger = logging.getLogger(__name__)

law_code_to_model_map = {
    'ors': models.OregonRevisedStatute
}


def get_model(law_code):
    return law_code_to_model_map[law_code]


def fetch_by_code(law_code, version=None):
    model = get_model(law_code)
    if not version:
        return model.objects
    else:
        version_key = 'texts.' + str(version)
        return model.objects(__raw__={
            version_key: {'$exists': True}
        })


def fetch_law(law_code, subsection):
    model = get_model(law_code)
    return model.objects(subsection=subsection).first()


def get_or_create_law(subsection, law_code):
    model = get_model(law_code)
    obj, created = model.objects.get_or_create(subsection=subsection)
    return obj
