# coding: utf-8
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

BaseModel = declarative_base()


def get_engine(database_absolute_path: str):
    return create_engine(
        'sqlite:///{}'.format(database_absolute_path),
        echo=False,
    )


def get_session(engine):
    return sessionmaker(bind=engine)
