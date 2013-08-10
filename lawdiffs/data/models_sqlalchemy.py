import logging
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base

logger = logging.getLogger(__name__)

Base = declarative_base()


class LawCode(Base):
    __tablename__ = 'law_code'
    id = Column(Integer, primary_key=True)
    law_code = Column(String)

    def __init__(self, law_code):
        self.law_code = law_code

    def __str__(self):
        return '<LawCode {} ({})>'.format(self.id, self.law_code)


class LawDivision(Base):
    __tablename__ = 'law_division'
    id = Column(Integer, primary_key=True)
    title = Column(String)
    law_code = Column(String)
    children = relationship('Law', backref='law_division')


class LawVersion(Base):
    __tablename__ = 'law_version'

    law_id = Column(Integer, ForeignKey('law.id'))
    version = Column(String)
    title = Column(String)
    text = Column(String)


class Law(Base):
    __tablename__ = 'law'

    id = Column(Integer, primary_key=True)
    law_code = Column(String)
    subsection = Column(String)
    division_id = Column(Integer, ForeignKey('law_division.id'))
    versions = relationship('LawVersion', backref='law')

    def __init__(self, law_code, subsection):
        self.law_code = law_code
        self.subsection = subsection
