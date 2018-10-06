# coding: utf-8
import pytest
from aioresponses import aioresponses

from tracimtools.client.http import HttpClient
from tracimtools.client.instance import Instance
from tracimtools.tsync.tree import RemoteTree


@pytest.fixture(scope='function')
def instance() -> Instance:
    return Instance(
        'tracim.local',
        port=80,
        base_path='/api/v2/',
        https=False,
    )


@pytest.fixture(scope='function')
def client(instance) -> HttpClient:
    return HttpClient(instance)


@pytest.fixture(scope='function')
def remote_tree(client):
    return RemoteTree(client)


@pytest.mark.asyncio
async def test_remote_tree_elements__simple_case(remote_tree):
    with aioresponses() as rmock:
        rmock.get(
            'http://tracim.local:80/api/v2/workspaces',
            status=200,
            payload=[
                {
                    "label": "Intranet",
                    "workspace_id": 1,
                },
            ],
        )
        rmock.get(
            'http://tracim.local:80/api/v2/workspaces/1/contents',
            status=200,
            payload=[
                {
                    "content_id": 6,
                    "content_type": "html-document",
                    "label": "Intervention Report 12",
                    "parent_id": None,
                }
            ]
        )

        elements = [e async for e in remote_tree.elements]
        assert ['Intranet/Intervention Report 12'] == elements


@pytest.mark.asyncio
async def test_remote_tree_elements__file_in_folder(remote_tree):
    with aioresponses() as rmock:
        rmock.get(
            'http://tracim.local:80/api/v2/workspaces',
            status=200,
            payload=[
                {
                    "label": "Intranet",
                    "workspace_id": 1,
                },
            ],
        )
        rmock.get(
            'http://tracim.local:80/api/v2/workspaces/1/contents',
            status=200,
            payload=[
                {
                    "content_id": 1,
                    "content_type": "folder",
                    "label": "Interventions",
                    "parent_id": None,
                },
                {
                    "content_id": 6,
                    "content_type": "html-document",
                    "label": "Report 12",
                    "parent_id": 1,
                }
            ]
        )

        elements = [e async for e in remote_tree.elements]
        assert [
                   'Intranet/Interventions',
                   'Intranet/Interventions/Report 12',
               ] == elements


@pytest.mark.asyncio
async def test_remote_tree_elements__file_in_folders(remote_tree):
    with aioresponses() as rmock:
        rmock.get(
            'http://tracim.local:80/api/v2/workspaces',
            status=200,
            payload=[
                {
                    "label": "Intranet",
                    "workspace_id": 1,
                },
            ],
        )
        rmock.get(
            'http://tracim.local:80/api/v2/workspaces/1/contents',
            status=200,
            payload=[
                {
                    "content_id": 1,
                    "content_type": "folder",
                    "label": "Interventions",
                    "parent_id": None,
                },
                {
                    "content_id": 2,
                    "content_type": "folder",
                    "label": "South",
                    "parent_id": 1,
                },
                {
                    "content_id": 6,
                    "content_type": "html-document",
                    "label": "Report 12",
                    "parent_id": 2,
                }
            ]
        )

        elements = [e async for e in remote_tree.elements]
        assert [
                   'Intranet/Interventions',
                   'Intranet/Interventions/South',
                   'Intranet/Interventions/South/Report 12',
               ] == elements
