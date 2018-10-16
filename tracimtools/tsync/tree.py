# coding: utf-8
import os
import typing
import time
import datetime

from tracimtools.client.http import HttpClient
from tracimtools.client.session import BasicAuthSession
from tracimtools.model.content import Content
from tracimtools.tsync.index.manager import IndexManager
from tracimtools.tsync.index.model import ContentModel


class TreeElement(object):
    def __init__(
            self,
            content_id: int,
            file_path: str,
            content_type: str,
            modified_timestamp: int,
    ) -> None:
        self._content_id = content_id
        self._file_path = file_path
        self._content_type = content_type
        self._modified_timestamp = modified_timestamp

    @property
    def content_id(self) -> int:
        return self._content_id

    @property
    def file_path(self) -> str:
        return self._file_path

    @property
    def content_type(self) -> str:
        return self._content_type

    @property
    def modified_timestamp(self) -> float:
        return self._modified_timestamp

    @modified_timestamp.setter
    def modified_timestamp(self, value: int) -> None:
        self._modified_timestamp = value


class LocalTree(object):
    def __init__(self, folder_absolute_path: str) -> None:
        self._folder_path = folder_absolute_path
        self._index = IndexManager(folder_absolute_path)
        self._elements_by_path = None  # type: typing.Dict[str, TreeElement]

    @property
    def index(self) -> IndexManager:
        return self._index

    @property
    def elements_by_path(self) -> typing.Dict[str, TreeElement]:
        if self._elements_by_path is not None:
            return self._elements_by_path

        # TODO BS 2018-10-16: Specialize exception
        raise Exception('elements must by synchronized first')

    @property
    def elements(self) -> typing.Iterable[TreeElement]:
        if self._elements_by_path is not None:
            return self._elements_by_path.values()

        # TODO BS 2018-10-16: Specialize exception
        raise Exception('elements must by synchronized first')

    def _get_tree_element_from_model(
        self,
        content_model: ContentModel,
    ) -> TreeElement:
        return TreeElement(
            content_id=content_model.remote_id,
            file_path=content_model.local_path,
            content_type=content_model.content_type,
            modified_timestamp=content_model.local_modified_timestamp,
        )

    def _excluded(self, path: str) -> bool:
        return path.endswith('.index.sqlite')

    def synchronize(self) -> None:
        def scantree(path: str):
            for entry in os.scandir(path):
                if entry.is_dir(follow_symlinks=False):
                    yield entry.path
                    yield from scantree(entry.path)
                elif not self._excluded(entry.path):
                    # TODO BS 2018-10-15: Manage bug case where not in index
                    content_model = self._index.get_one_from_path(entry.path)
                    tree_element = self._get_tree_element_from_model(content_model)  # nopep8

                    # Local last modified timestamp must be local reallity
                    tree_element.modified_timestamp = os.path.getmtime(
                        tree_element.file_path,
                    )

                    yield tree_element

        self._elements_by_path = {}
        for element in scantree(self._folder_path):
            self._elements_by_path[element.file_path] = element


class RemoteTree(object):
    def __init__(self, client: HttpClient) -> None:
        self._client = client

    @property
    async def elements(
        self,
    ) -> typing.AsyncIterable[TreeElement]:
        # TODO BS 2018-10-06: should not be here ...
        session = BasicAuthSession('admin@admin.admin', 'admin@admin.admin')
        content_cache = {}
        todo = []

        def get_extension(content_: Content) -> str:
            if content_.content_type == "html-document":
                return ".html"
            elif content_.content_type == "file":
                # FIXME BS 2018-10-09: extension not available for now
                # HARDCODED
                return ".txt"
            elif content_.content_type == "folder":
                return ''
            else:
                raise NotImplementedError(
                    'Content type "{}" not supported'.format(
                        content_.content_type,
                    )
                )

        async for workspace in self._client.get_workspaces(session):
            async for content in self._client.get_contents(session, workspace.workspace_id):

                content_cache[content.content_id] = content
                # TODO BS 2018-10-11: FASTER if modified in contents endpoint
                modified_timestamp = time.mktime(
                    datetime.datetime.strptime(
                        content.modified,
                        "%Y-%m-%dT%H:%M:%S.%fZ"
                    ).timetuple()
                )
                try:
                    yield TreeElement(
                        content.content_id,
                        os.path.join(*get_complete_path(get_extension,
                                                        content_cache,
                                                        workspace, content)),
                        content_type=content.content_type,
                        modified_timestamp=int(modified_timestamp),
                    )
                # TODO BS 2018-10-11: Manage this case with correct exception
                except ZeroDivisionError:
                    todo.append(content)

            for content in todo:
                yield TreeElement(
                    content.content_id,
                    os.path.join(*get_complete_path(get_extension,
                                                    content_cache, workspace,
                                                    content)),
                    content.content_type,
                )


def get_complete_path(get_extension, content_cache, workspace_, content_) -> typing.List[str]:
    if not content_.parent_id:
        return [
            workspace_.label,
            content_.label + get_extension(content_),
        ]

    path_items = [content_.label + get_extension(content_)]
    current_content = content_
    while current_content.parent_id:
        try:
            current_content = content_cache[current_content.parent_id]
        except KeyError:
            raise ZeroDivisionError()
        path_items.insert(0, current_content.label)

    path_items.insert(0, workspace_.label)

    return path_items
