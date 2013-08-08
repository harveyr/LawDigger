import inspect
import logging
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
import re

logger = logging.getLogger(__name__)

engine = create_engine(
    'postgresql://harvey:asdf@127.0.0.1/lawdigger',
    echo=True)
Base = declarative_base()

class Law(Base):
    __tablename__ = 'Laws'

    id = Column(Integer, primary_key = True)
    subsection = Column(String)

    def __init__(self, subsection):
        self.subsection = subsection

Base.metadata.create_all(engine)
