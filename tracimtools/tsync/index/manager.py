# coding: utf-8
import os

from sqlalchemy.orm import sessionmaker, Session

from tracimtools.tsync.index.db import BaseModel, get_engine, get_session
from tracimtools.tsync.index.model import ContentModel


class IndexManager(object):
    def __init__(self, folder_absolute_path: str) -> None:
        self._db_engine = get_engine(
            os.path.join(folder_absolute_path, '.index.sqlite'),
        )
        session_maker = sessionmaker(autoflush=False, bind=self._db_engine)
        self._db_session = session_maker()
        BaseModel.metadata.create_all(self._db_engine)

    @property
    def session(self) -> Session:
        return self._db_session

    def add_file(
        self,
        relative_path,
        remote_id,
        remote_modified_timestamp,
        local_modified_timestamp,
        auto_commit: bool = False,
    ) -> ContentModel:
        content = ContentModel()
        content.local_path = relative_path
        content.remote_id = remote_id
        content.remote_modified_timestamp = remote_modified_timestamp
        content.local_modified_timestamp = local_modified_timestamp

        self._db_session.add(content)
        if auto_commit:
            self._db_session.commit()

        return content

    def commit(self) -> None:
        self._db_session.commit()

    def get_one_from_path(self, path: str) -> ContentModel:
        return self._db_session.query(ContentModel)\
            .filter(ContentModel.local_path == path)\
            .one()

    def update_file(
        self,
        file_path: str,
        remote_modified_timestamp: int,
        local_modified_timestamp: int,
        auto_commit: bool = False,
    ) -> ContentModel:
        content = self.get_one_from_path(file_path)
        content.local_modified_timestamp = local_modified_timestamp
        content.remote_modified_timestamp = remote_modified_timestamp

        self._db_session.add(content)
        if auto_commit:
            self._db_session.commit()

        return content
