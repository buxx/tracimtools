# coding: utf-8
import argparse
import asyncio

from tracimtools.client.http import HttpClient
from tracimtools.tsync.tree import LocalTree
from tracimtools.tsync.tree import RemoteTree


def main(
        local_folder_path: str,
        tracim_instance: str,
        email: str,
        password: str,
        base_path: str,
) -> None:
    local_tree = LocalTree(local_folder_path)
    for element in local_tree.elements:
        print(element)

    print('...')
    print('...')

    async def remote():
        from tracimtools.client.instance import Instance
        remote_tree = RemoteTree(HttpClient(Instance('latest.tracim.fr', 6543, https=False)))
        async for element in remote_tree.elements:
            print(element)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(remote())
    loop.close()


def cli():
    # TODO BS 2018-10-06: how avoid password ? @GM token ?
    """
    tsync . my.trac.im --email admin@admin.admin --password admin@admin.admin [--base-path=/api/v2/]
    """
    parser = argparse.ArgumentParser(description='Synchronize local folder with tracim instance')
    parser.add_argument('local_folder_path', type=str, help='local folder')
    parser.add_argument('tracim_instance', type=str, help='tracim instance base url')
    parser.add_argument('--email', '-e', type=str, help='user email')
    parser.add_argument('--password', '-p', type=str, help='user password')
    parser.add_argument('--base-path', type=str, help='eg. /api/v2/', default='/api/v2/')

    args = parser.parse_args()

    main(
        args.local_folder_path,
        args.tracim_instance,
        email=args.email,
        password=args.password,
        base_path=args.base_path,
    )


if __name__ == '__main__':
    cli()
