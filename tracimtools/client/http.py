# condig: utf-8
import typing
from io import BytesIO

import aiohttp

from tracimtools.client.instance import Instance
from tracimtools.client.session import Session
from tracimtools.model.content import Content
from tracimtools.model.workspace import Workspace


class HttpClient(object):
    def __init__(self, instance: Instance) -> None:
        self._instance = instance

    async def get_workspaces(self, session: Session) -> typing.Generator[Workspace, None, None]:
        # url = self._instance.urls.workspaces
        # TODO BS 2018-10-06: implement urls
        url = self._instance.base_url + 'workspaces'

        async with aiohttp.ClientSession() as aiohttp_session:
            async with aiohttp_session.get(url, **session.request_kwargs) as resp:
                for workspace_dict in await resp.json():
                    yield Workspace(**workspace_dict)

    async def get_contents(self, session: Session, workspace_id: int) -> typing.Generator[Content, None, None]:
        # url = self._instance.urls.workspace(workspace_id).contents
        # TODO BS 2018-10-06: implement urls
        url = self._instance.base_url + 'workspaces/{}/contents'.format(workspace_id)

        async with aiohttp.ClientSession() as aiohttp_session:
            async with aiohttp_session.get(url, **session.request_kwargs) as resp:
                content_list = await resp.json()
                for content_dict in content_list:
                    yield Content(**content_dict)

    def get_content_bytes(self, workspace_id: int, content_id: int) -> BytesIO:
        return BytesIO(b'')
