import os

import pytest
from _pytest.fixtures import FixtureRequest

from tracimtools.client.http import HttpClient
from tracimtools.client.instance import Instance
from tracimtools.tsync.index.manager import IndexManager
from tracimtools.tsync.tree import RemoteTree

one_workspace_list = [
    {
        "label": "Intranet",
        "workspace_id": 1,
    },
]
one_document_without_folder = [
    {
        "content_id": 6,
        "content_type": "html-document",
        "label": "Intervention Report 12",
        "modified": "2018-10-15T15:42:40.710Z",
        "parent_id": None,
    }
]
one_document_in_folder = [
    {
        "content_id": 1,
        "content_type": "folder",
        "label": "Interventions",
        "modified": "2018-10-15T15:42:40.710Z",
        "parent_id": None,
    },
    {
        "content_id": 6,
        "content_type": "html-document",
        "label": "Report 12",
        "modified": "2018-10-15T15:42:40.710Z",
        "parent_id": 1,
    }
]
one_document_in_two_folders = [
    {
        "content_id": 1,
        "content_type": "folder",
        "label": "Interventions",
        "modified": "2018-10-15T15:42:40.710Z",
        "parent_id": None,
    },
    {
        "content_id": 2,
        "content_type": "folder",
        "label": "South",
        "modified": "2018-10-15T15:42:40.710Z",
        "parent_id": 1,
    },
    {
        "content_id": 6,
        "content_type": "html-document",
        "label": "Report 12",
        "modified": "2018-10-15T15:42:40.710Z",
        "parent_id": 2,
    }
]


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


@pytest.fixture(scope='function')
def empty_index(request: FixtureRequest, empty_test_dir_path: str):
    absolute_tree_path = getattr(request, 'param', {}).get(
        "absolute_tree_path",
        empty_test_dir_path,
    )
    os.unlink(os.path.join(absolute_tree_path, '.index.sqlite'))
    index = IndexManager(folder_absolute_path=empty_test_dir_path)
    yield index
