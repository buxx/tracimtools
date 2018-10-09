# coding: utf-8
import os
import typing

from tracimtools.tsync.sync.pending import PendingAction
from tracimtools.tsync.tree import LocalTree
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

        from_remote_actions = await self.execute_new_from_remote()
        pending_actions.extend(from_remote_actions)

        return pending_actions

    async def execute_new_from_remote(self) -> typing.List[PendingAction]:
        pending_actions = []  # type: typing.List[PendingAction]
        local_elements = [e for e in self._local_tree.elements]

        async for remote_element in self._remote_tree.elements:
            if remote_element.file_path not in local_elements:
                remote_element_path = os.path.join(
                    self._local_tree._folder_path,
                    remote_element.file_path,
                )
                remote_element_dir_path = '/' + os.path.join(*remote_element_path.split('/')[0:-1])

                if not os.path.exists(remote_element_dir_path):
                    os.makedirs(remote_element_dir_path)

                # TODO BS 2018-10-11: Must check if there is no conflict
                if remote_element.content_type in ["html-document", "file"]:
                    with open(remote_element_path, 'w+') as file:
                        file.write('')

                    self._local_tree.index.add_file(
                        remote_element_path,
                        remote_id=remote_element.content_id,
                        remote_modified_timestamp=remote_element.modified_timestamp,
                        # local_modified_timestamp=os.path.getmtime(remote_element_path),
                        local_modified_timestamp=remote_element.modified_timestamp,
                    )

        self._local_tree.index.commit()
        return pending_actions
