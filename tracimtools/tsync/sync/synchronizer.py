# coding: utf-8
import os
import typing

from tracimtools.tsync.sync.pending import PendingAction
from tracimtools.tsync.tree import LocalTree, TreeElement
from tracimtools.tsync.tree import RemoteTree


class Synchronizer(object):
    def __init__(
            self,
            local_tree: LocalTree,
            remote_tree: RemoteTree,
    ) -> None:
        self._local_tree = local_tree
        self._remote_tree = remote_tree

    async def run(self) -> typing.List[PendingAction]:
        pending_actions = []  # type: typing.List[PendingAction]

        from_remote_actions = await self.synchronize_from_remote()
        pending_actions.extend(from_remote_actions)

        return pending_actions

    async def synchronize_from_remote(self) -> typing.List[PendingAction]:
        pending_actions = []  # type: typing.List[PendingAction]
        local_elements_by_path = self._local_tree.elements_by_path

        async for remote_element in self._remote_tree.elements:

            # New from remote
            if remote_element.file_path not in local_elements_by_path:
                self._sync_new_file_from_remote(remote_element)

            # Update from remote
            else:
                actions = self._sync_updated_file_from_remote(remote_element)
                pending_actions.extend(actions)

        self._local_tree.index.commit()
        return pending_actions

    def _sync_new_file_from_remote(self, remote_element: TreeElement):
        remote_element_path = os.path.join(
            self._local_tree._folder_path,
            remote_element.file_path,
        )
        remote_element_dir_path = '/' + os.path.join(
            *remote_element_path.split('/')[0:-1])
        os.makedirs(remote_element_dir_path, exist_ok=True)

        # TODO BS 2018-10-11: Must check if there is no conflict
        if remote_element.content_type in ["html-document", "file"]:
            with open(remote_element_path, 'w+') as file:
                file.write('')

            self._local_tree.index.add_file(
                remote_element_path,
                remote_id=remote_element.content_id,
                remote_modified_timestamp=remote_element.modified_timestamp,
                local_modified_timestamp=remote_element.modified_timestamp,
            )

    def _sync_updated_file_from_remote(
            self, remote_element: TreeElement,
    ) -> typing.List[PendingAction]:
        remote_element_path = remote_element.file_path
        local_element = self._local_tree.elements_by_path[remote_element_path]

        return []
