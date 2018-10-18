# coding: utf-8
import os
import shutil

import pytest
from aioresponses import aioresponses

from tests.fixtures import one_document_without_folder, one_document_in_folder, one_document_in_two_folders
from tests.fixtures import one_workspace_list
from tracimtools.client.utils import str_time_to_timestamp
from tracimtools.tsync.index.manager import IndexManager
from tracimtools.tsync.index.model import ContentModel
from tracimtools.tsync.sync.pending import AcceptRemote
from tracimtools.tsync.sync.synchronizer import Synchronizer
from tracimtools.tsync.tree import LocalTree
from tracimtools.tsync.tree import RemoteTree


@pytest.fixture(scope='function')
def empty_test_dir_path():
    # TODO BS 2018-10-09: Make this configurable
    dir_path = '/tmp/tsync_tests/local_folder'
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    shutil.rmtree(dir_path)
    os.mkdir(dir_path)
    return dir_path


@pytest.fixture(scope='function')
def local_tree(empty_test_dir_path):
    tree = LocalTree(empty_test_dir_path)
    tree.build()
    yield tree


@pytest.fixture(scope='function')
def synchronizer(
        empty_test_dir_path: str,
        remote_tree: RemoteTree,
        local_tree: LocalTree,
) -> Synchronizer:
    return Synchronizer(
        local_tree,
        remote_tree,
    )


@pytest.fixture(scope='function')
def intervention_report_12__no_folder__already_present(
    empty_test_dir_path: str,
    local_tree: LocalTree,
) -> str:
    # Create file on disk
    absolute_file_dir_path = os.path.join(
        empty_test_dir_path,
        'Intranet',
    )
    absolute_file_path = os.path.join(
        absolute_file_dir_path,
        'Intervention Report 12.html',
    )
    relative_file_path = os.path.join(
        'Intranet',
        'Intervention Report 12.html',
    )

    os.makedirs(absolute_file_dir_path)
    with open(absolute_file_path, 'w+') as f:
        f.write('')

    # Add it in index (we are simulating update conflict)
    local_tree.index.add_file(
        relative_path=relative_file_path,
        local_modified_timestamp=str_time_to_timestamp(
            one_document_without_folder[0]["modified"],
        ),
        remote_id=one_document_without_folder[0]["content_id"],
        remote_modified_timestamp=str_time_to_timestamp(
            one_document_without_folder[0]["modified"],
        ),
    )
    local_tree.index.commit()
    local_tree.build()

    return absolute_file_path


@pytest.mark.asyncio
async def test_sync__from_scratch__one_file(
        empty_test_dir_path: str,
        synchronizer: Synchronizer,
        empty_index: IndexManager,
):
    with aioresponses() as rmock:
        rmock.get(
            'http://tracim.local:80/api/v2/workspaces',
            status=200,
            payload=one_workspace_list,
        )
        rmock.get(
            'http://tracim.local:80/api/v2/workspaces/1/contents',
            status=200,
            payload=one_document_without_folder,
        )

        pending_actions = [a async for a in synchronizer.run()]
        assert not pending_actions
        assert os.path.isfile(
            os.path.join(
                empty_test_dir_path,
                'Intranet',
                'Intervention Report 12.html'
            ),
        )

        contents = empty_index.session.query(ContentModel).all()
        assert 1 == len(contents)
        assert 6 == contents[0].remote_id
        assert 1539610960 == contents[0].local_modified_timestamp
        assert 1539610960 == contents[0].remote_modified_timestamp
        assert empty_test_dir_path + '/Intranet/Intervention Report 12.html' == contents[0].local_path  # nopep8


@pytest.mark.asyncio
async def test_sync__from_scratch__one_file_update_and_conflict(
    empty_test_dir_path: str,
    synchronizer: Synchronizer,
    empty_index: IndexManager,
    intervention_report_12__no_folder__already_present: str,
):
    index = empty_index
    file_path = intervention_report_12__no_folder__already_present

    # Simulate change since last sync
    with open(file_path, 'w+') as f:
        f.write('')

    with aioresponses() as rmock:
        rmock.get(
            'http://tracim.local:80/api/v2/workspaces',
            status=200,
            payload=one_workspace_list,
        )
        rmock.get(
            'http://tracim.local:80/api/v2/workspaces/1/contents',
            status=200,
            payload=one_document_without_folder,
        )

        pending_actions = [a async for a in synchronizer.run()]
        assert pending_actions
        assert 1 == len(pending_actions)

    # Before accept remote solution
    assert os.path.isfile(
        os.path.join(
            empty_test_dir_path,
            'Intranet',
            'Intervention Report 12.html'
        ),
    )

    # timestamp of file is currently not touched
    remote_timestamp = str_time_to_timestamp(
        one_document_without_folder[0]["modified"],
    )

    contents = empty_index.session.query(ContentModel).all()
    assert 1 == len(contents)
    assert 6 == contents[0].remote_id
    assert remote_timestamp == contents[0].local_modified_timestamp
    assert remote_timestamp == contents[0].remote_modified_timestamp
    assert 'Intranet/Intervention Report 12.html' == contents[0].local_path

    solutions = pending_actions[0].get_solutions()
    assert 1 == len(solutions)
    assert isinstance(solutions[0], AcceptRemote)

    # Accept remote
    pending_actions[0].resolve(solutions[0])

    # File updated with remote data and timestamp
    contents = empty_index.session.query(ContentModel).all()
    assert 1 == len(contents)
    assert 6 == contents[0].remote_id
    assert remote_timestamp == contents[0].local_modified_timestamp
    assert remote_timestamp == contents[0].remote_modified_timestamp
    assert 'Intranet/Intervention Report 12.html' == contents[0].local_path


@pytest.mark.asyncio
async def test_sync__from_scratch__one_file_with_one_folder(
        empty_test_dir_path: str,
        synchronizer: Synchronizer,
        empty_index: IndexManager,
):
    with aioresponses() as rmock:
        rmock.get(
            'http://tracim.local:80/api/v2/workspaces',
            status=200,
            payload=one_workspace_list,
        )
        rmock.get(
            'http://tracim.local:80/api/v2/workspaces/1/contents',
            status=200,
            payload=one_document_in_folder,
        )

        pending_actions = [a async for a in synchronizer.run()]
        assert not pending_actions
        assert os.path.isfile(
            os.path.join(
                empty_test_dir_path,
                'Intranet',
                'Interventions',
                'Report 12.html'
            ),
        )

        contents = empty_index.session.query(ContentModel).all()
        assert 1 == len(contents)
        assert 6 == contents[0].remote_id
        assert 1539610960 == contents[0].local_modified_timestamp
        assert 1539610960 == contents[0].remote_modified_timestamp
        assert empty_test_dir_path + '/Intranet/Interventions/Report 12.html' == contents[0].local_path  # nopep8


@pytest.mark.asyncio
async def test_sync__from_scratch__one_file_with_two_folder(
        empty_test_dir_path: str,
        synchronizer: Synchronizer,
        empty_index: IndexManager,
):
    with aioresponses() as rmock:
        rmock.get(
            'http://tracim.local:80/api/v2/workspaces',
            status=200,
            payload=one_workspace_list,
        )
        rmock.get(
            'http://tracim.local:80/api/v2/workspaces/1/contents',
            status=200,
            payload=one_document_in_two_folders,
        )

        pending_actions = [a async for a in synchronizer.run()]
        assert not pending_actions
        assert os.path.isfile(
            os.path.join(
                empty_test_dir_path,
                'Intranet',
                'Interventions',
                'South',
                'Report 12.html'
            ),
        )

        contents = empty_index.session.query(ContentModel).all()
        assert 1 == len(contents)
        assert 6 == contents[0].remote_id
        assert 1539610960 == contents[0].local_modified_timestamp
        assert 1539610960 == contents[0].remote_modified_timestamp
        assert empty_test_dir_path + '/Intranet/Interventions/South/Report 12.html' == contents[0].local_path  # nopep8
