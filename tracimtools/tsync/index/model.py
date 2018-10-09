# coding: utf-8
from sqlalchemy import Column, String, Integer

from tracimtools.tsync.index.db import BaseModel


class ContentModel(BaseModel):
    __tablename__ = 'content'

    local_path = Column(String, primary_key=True)
    remote_id = Column(Integer, primary_key=True)
    remote_modified_timestamp = Column(Integer)
    local_modified_timestamp = Column(Integer)
