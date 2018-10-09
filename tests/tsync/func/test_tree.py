# coding: utf-8
import pytest
from aioresponses import aioresponses

from tests.fixtures import one_document_in_folder
from tests.fixtures import one_document_in_two_folders
from tests.fixtures import one_document_without_folder
from tests.fixtures import one_workspace_list


@pytest.mark.asyncio
async def test_remote_tree_elements__simple_case(remote_tree):
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

        elements = [e.file_path async for e in remote_tree.elements]
        assert ['Intranet/Intervention Report 12.html'] == elements


@pytest.mark.asyncio
async def test_remote_tree_elements__file_in_folder(remote_tree):
    with aioresponses() as rmock:
        rmock.get(
            'http://tracim.local:80/api/v2/workspaces',
            status=200,
            payload=one_workspace_list
        )
        rmock.get(
            'http://tracim.local:80/api/v2/workspaces/1/contents',
            status=200,
            payload=one_document_in_folder,
        )

        elements = [e.file_path async for e in remote_tree.elements]
        assert [
                   'Intranet/Interventions',
                   'Intranet/Interventions/Report 12.html',
               ] == elements


@pytest.mark.asyncio
async def test_remote_tree_elements__file_in_folders(remote_tree):
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

        elements = [e.file_path async for e in remote_tree.elements]
        assert [
                   'Intranet/Interventions',
                   'Intranet/Interventions/South',
                   'Intranet/Interventions/South/Report 12.html',
               ] == elements
