import logging

from . import laws as da_laws
from .. import law_codes
from .. import models

logger = logging.getLogger(__name__)

law_code = law_codes.OREGON_REVISED_STATUTES


def get_or_create_volume(version, volume_str):
    obj = da_laws.get_or_create_division(
        law_code=law_code, version=version, division=volume_str)
    if obj.leaf is not False:
        obj.leaf = False
        obj.save()

    return obj


def get_or_create_chapter(volume, chapter_str):
    if not isinstance(volume, models.LawDivision):
        raise Exception('I want LawDivision. I got {}'.format(volume))

    obj = da_laws.get_or_create_division(
        parent_id=volume.id, law_code=volume.law_code,
        version=volume.version, division=chapter_str)
    if obj.leaf is not True:
        obj.leaf = True
        obj.save()

    return obj


def create_statute(chapter, subsection, title, text):
    law = da_laws.create_law_in_division(
        division=chapter,
        subsection=subsection,
        title=title,
        text=text)
    logger.info('Created ORS: {}'.format(law))
    return law
