# import mongoengine as moe
from .. import models
import logging

logger = logging.getLogger(__name__)

state_model_map = {
    'or': models.OregonRevisedStatute
}


def fetch_laws_by_state_code(state_code):
    model = state_model_map[state_code]
    return model.objects


def fetch_law(state_code, id_):
    model = state_model_map[state_code]
    return model.objects(id=id_).first()


def get_or_create_law(subsection, state_code):
    model = state_model_map[state_code]
    obj, created = model.objects.get_or_create(subsection=subsection)
    return obj
