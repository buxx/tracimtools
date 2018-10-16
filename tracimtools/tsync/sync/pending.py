# coding: utf-8
import os
import typing

from tracimtools.client.http import HttpClient
from tracimtools.tsync.index.manager import IndexManager
from tracimtools.tsync.tree import TreeElement


class SolutionInterface(object):
    def get_description(self) -> str:
        raise NotImplementedError()

    def get_choice_letter(self) -> str:
        raise NotImplementedError()

    def execute(
        self,
        local_element: TreeElement,
        remote_element: TreeElement,
    ) -> None:
        raise NotImplementedError()


class BaseSolution(SolutionInterface):
    description = NotImplemented
    choice_letter = NotImplemented

    def __init__(
        self,
        index_manager: IndexManager,
        client: HttpClient,
    ) -> None:
        self._index_manager = index_manager
        self._client = client

    def get_description(self) -> str:
        return self.description

    def get_choice_letter(self) -> str:
        return self.choice_letter

    def execute(
        self,
        local_element: TreeElement,
        remote_element: TreeElement,
    ) -> None:
        raise NotImplementedError()


class AcceptRemote(BaseSolution):
    description = 'Accept remote file'
    choice_letter = 'R'

    def execute(
        self,
        local_element: TreeElement,
        remote_element: TreeElement,
    ) -> None:
        with open(local_element.file_path, 'wb+') as file_:
            remote_file_content = self._client.get_content_bytes(
                remote_element.workspace_id,
                remote_element.content_id,
            )
            file_.write(remote_file_content)

        self._index_manager.update_file(
            local_element.file_path,
            remote_modified_timestamp=remote_element.modified_timestamp,
            local_modified_timestamp=os.path.getmtime(
                local_element.file_path,
            )
        )


class PendingAction(object):
    def __init__(
        self,
        local_element: TreeElement,
        remote_element: TreeElement,
        solutions: typing.List[SolutionInterface],
    ) -> None:
        self._local_element = local_element
        self._remote_element = remote_element
        self._solutions = solutions

    @property
    def local_element(self) -> TreeElement:
        return self._local_element

    @property
    def remote_element(self) -> TreeElement:
        return self._remote_element

    def get_solutions(self) -> typing.List[SolutionInterface]:
        return self._solutions

    def resolve(self, solution: SolutionInterface):
        solution.execute(self._local_element, self._remote_element)
