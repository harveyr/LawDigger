from .. import models
from ...data import cache, encoder
from ..access import Session
import logging
import re

logger = logging.getLogger(__name__)

session = Session()


class Law_Data_Exception(Exception):
    pass


def create_law_code(law_code, ignore=False):
    existing = session.query(models.LawCode).filter(
        models.LawCode.law_code == law_code).first()
    if existing:
        if not ignore:
            raise Law_Data_Exception(
                'law code already exists: {}'.format(existing))
        else:
            return existing
    else:
        obj = models.LawCode(law_code)
        session.add(obj)
        session.commit()


def set_law_version(law, version, title='', text=''):
    # title = encoder.utf8(title)
    # text = encoder.utf8(text)

    model = models.LawVersion
    version = session.query(model)\
        .filter(model.law == law).first()
    if not version:
        version = model()
        session.add(version)
    version.title = title
    version.text = text

    law.versions.add(version)
    session.commit()


def get_or_create_law(law_code, subsection):
    model = models.Law
    existing = session.query(model)\
        .filter(model.law_code == law_code)\
        .filter(model.subsection == subsection)\
        .first()
    if existing:
        return existing
    else:
        law = model(law_code=law_code, subsection=subsection)
        session.add(law)
        session.commit()
        return law
# def get_or_create_division()
