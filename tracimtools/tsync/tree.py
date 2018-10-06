# coding: utf-8
import os
import typing

from tracimtools.client.http import HttpClient
from tracimtools.client.session import BasicAuthSession


class LocalTree(object):
    def __init__(self, folder_path: str) -> None:
        self._folder_path = folder_path

    @property
    def elements(self) -> typing.Generator[str, None, None]:
        def scantree(path: str):
            for entry in os.scandir(path):
                if entry.is_dir(follow_symlinks=False):
                    yield entry.path
                    yield from scantree(entry.path)
                else:
                    yield entry.path
    
        return scantree(self._folder_path)


class RemoteTree(object):
    def __init__(self, client: HttpClient) -> None:
        self._client = client

    @property
    async def elements(self) -> typing.Generator[str, None, None]:
        # TODO BS 2018-10-06: should not be here ...
        session = BasicAuthSession('admin@admin.admin', 'admin@admin.admin')
        content_cache = {}
        todo = []

        def get_complete_path(workspace, content) -> typing.List[str]:
            if not content.parent_id:
                return [workspace.label, content.label]

            path_items = [content.label]
            while content.parent_id:
                content = content_cache[content.parent_id]
                path_items.insert(0, content.label)

            path_items.insert(0, workspace.label)

            return path_items

        async for workspace in self._client.get_workspaces(session):
            async for content in self._client.get_contents(session, workspace.workspace_id):

                content_cache[content.content_id] = content
                try:
                    yield os.path.join(*get_complete_path(workspace, content))
                except ZeroDivisionError:
                    todo.append(content)

            for content in todo:
                yield os.path.join(*get_complete_path(workspace, content))
