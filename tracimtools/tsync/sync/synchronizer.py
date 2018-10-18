# coding: utf-8
import os
import typing

from tracimtools.tsync.sync.pending import PendingAction, AcceptRemote, \
    AcceptLocal
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

    async def run(self) -> typing.Generator[PendingAction, None, None]:
        async for action in self.synchronize_from_remote():
            yield action

    async def synchronize_from_remote(
        self,
    ) -> typing.Generator[PendingAction, None, None]:
        async for remote_element in self._remote_tree.elements:
            if not self._excluded_element(remote_element):

                # Process remote element and yield eventual pending actions
                async for pending_action in self._process_remote_element(
                    remote_element,
                ):
                    yield pending_action

    async def _process_remote_element(
        self,
        remote_element: TreeElement
    ) -> typing.Generator[PendingAction, None, None]:
        local_elements_by_path = self._local_tree.elements_by_path

        # New from remote
        if remote_element.file_path not in local_elements_by_path:
            await self._sync_new_file_from_remote(remote_element)

        # Update from remote
        else:
            async for action in self._sync_updated_file_from_remote(
                    remote_element,
            ):
                yield action

        # TODO BS 2018-10-16: We yielding, so maybe should commit at each
        self._local_tree.index.commit()

    def _excluded_element(self, remote_element: TreeElement) -> bool:
        return remote_element.content_type not in ["html-document", "file"]

    async def _sync_new_file_from_remote(self, remote_element: TreeElement):
        remote_element_path = os.path.join(
            self._local_tree._folder_path,
            remote_element.file_path,
        )
        remote_element_dir_path = '/' + os.path.join(
            *remote_element_path.split('/')[0:-1])
        os.makedirs(remote_element_dir_path, exist_ok=True)

        with open(remote_element_path, 'w+') as file:
            file.write('')  # FIXME BS 2018-10-16

            self._local_tree.index.add_file(
                remote_element_path,
                remote_id=remote_element.content_id,
                remote_modified_timestamp=remote_element.modified_timestamp,
                local_modified_timestamp=remote_element.modified_timestamp,
            )

    async def _sync_updated_file_from_remote(
        self, remote_element: TreeElement,
    ) -> typing.Generator[PendingAction, None, None]:
        element_file_path = remote_element.file_path
        absolute_file_path = os.path.join(
            self._local_tree.folder_path,
            element_file_path,
        )
        local_element = self._local_tree.elements_by_path[element_file_path]
        local_element_modified_fs = os.path.getmtime(absolute_file_path)
        local_element_modified_index = local_element.modified_timestamp
        local_element_is_modified = \
            local_element_modified_fs != local_element_modified_index \
            or not local_element.content_id

        # Simple update
        if local_element_is_modified:
            yield PendingAction(
                local_element=local_element,
                remote_element=remote_element,
                solutions=[
                    AcceptRemote(
                        client=self._remote_tree.client,
                        local_tree=self._local_tree,
                    ),
                    AcceptLocal(
                        client=self._remote_tree.client,
                        local_tree=self._local_tree,
                    ),
                ]
            )
        else:
            with open(absolute_file_path, 'w+') as file:
                file.write('')  # FIXME BS 2018-10-16
