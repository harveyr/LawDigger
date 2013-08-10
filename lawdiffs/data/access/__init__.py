from sqlalchemy.orm import sessionmaker
from ...data import sqlalchemy_engine

Session = sessionmaker(bind=sqlalchemy_engine)


