# import mongoengine as moe
from .. import models
import logging

logger = logging.getLogger(__name__)

state_model_map = {
    'or': models.OregonRevisedStatute
}


def fetch_by_state(state_code, version=None):
    model = state_model_map[state_code]
    if not version:
        return model.objects
    else:
        version_key = 'versions.' + str(version)
        return model.objects(__raw__={
            version_key: {'$exists': True}
        })

def fetch_law(state_code, id_):
    model = state_model_map[state_code]
    return model.objects(id=id_).first()


def get_or_create_law(subsection, state_code):
    model = state_model_map[state_code]
    obj, created = model.objects.get_or_create(subsection=subsection)
    return obj
