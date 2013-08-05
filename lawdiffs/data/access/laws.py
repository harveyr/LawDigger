# import mongoengine as moe
from .. import models
from ...data import cache
import logging

logger = logging.getLogger(__name__)

law_code_to_model_map = {
    'ors': {
        'statute': models.OregonRevisedStatute,
        'volume': models.ORSVolume,
        'chapter': models.ORSChapter
    }
}

float_subsections = ['ors']


def formatted_subsection(law_code, subsection):
    if law_code in float_subsections:
        return float(subsection)
    else:
        return subsection


def get_statute_model(law_code):
    return law_code_to_model_map[law_code]['statute']


def get_volume_model(law_code):
    return law_code_to_model_map[law_code]['volume']


def get_chapter_model(law_code):
    return law_code_to_model_map[law_code]['chapter']


def fetch_law(law_code, subsection):
    model = get_statute_model(law_code)
    return model.objects(subsection=subsection).first()


def fetch_ors_by_chapter(chapter):
    chapter_model = get_chapter_model('ors')
    chapter = chapter_model.objects(chapter=chapter).first()
    statute_model = get_statute_model('ors')
    statutes = statute_model.objects(id__in=chapter.statute_ids)
    return (chapter, statutes)


def fetch_previous_and_next_subsections(law_code, subsection):
    subsection = formatted_subsection(law_code, subsection)
    subsections = fetch_code_subsections(law_code)
    max_index = len(subsections) - 1
    idx = subsections.index(subsection)

    model = get_statute_model(law_code)
    if idx > 0:
        prev = model.subsection_float_to_string(subsections[idx - 1])
    else:
        prev = None

    if idx < max_index:
        next = model.subsection_float_to_string(subsections[idx + 1])
    else:
        next = None

    return (prev, next)


def fetch_volumes(law_code):
    model = get_volume_model(law_code)
    return model.objects().order_by('volume')


def get_or_create_volume(volume, law_code):
    model = get_volume_model(law_code)
    obj, created = model.objects.get_or_create(volume=volume)
    return obj


def get_or_create_chapter(chapter, volume, law_code):
    logger.setLevel(logging.DEBUG)
    model = get_chapter_model(law_code)
    obj, created = model.objects.get_or_create(
        chapter=chapter,
        volume_id=volume.id)
    return obj


def get_or_create_statute(subsection, law_code):
    model = get_statute_model(law_code)
    obj, created = model.objects.get_or_create(subsection=subsection)
    return obj



# def fetch_by_code(law_code, version=None):
#     model = get_statute_model(law_code)
#     if not version:
#         return model.objects
#     else:
#         version_key = 'texts.' + str(version)
#         return model.objects(__raw__={
#             version_key: {'$exists': True}
#         })


# def fetch_code_subsections(law_code):
#     cache_key = 'fetch_code_subsections_{}'.format(law_code)
#     cached = cache.get(cache_key)
#     if cached:
#         return cached

#     as_float = False
#     if law_code in ['ors']:
#         as_float = True

#     model = get_statute_model(law_code)
#     subsections = []
#     laws = model.objects.only('subsection').order_by('subsection')
#     for law in laws:
#         if as_float:
#             subsections.append(float(law.subsection))
#         else:
#             subsections.append(law.subsection)
#     subsections.sort()
#     cache.set(cache_key, subsections)
#     return subsections
