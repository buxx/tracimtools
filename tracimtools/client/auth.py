# coding: utf-8
import aiohttp

from tracimtools.client.instance import Instance
from tracimtools.client.session import BasicAuthSession


class Authentication(object):
    def __init__(self, instance: Instance) -> None:
        self._instance = instance

    def create_session(email: str, password: str) -> Session:
        url = self._instance.urls.session_login
        data = {'email': email, 'password': password}

        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=data) as resp:
                # TODO BS 2018-10-06: manage errors, expiration date
                resp_headers = resp.headers

        cookies = resp_headers['Set-Cookie'].split(';')
        session_key = cookies[0].split('=')[1]

        # TODO BS 2018-10-06: permit choose auth strategy
        return BasicAuthSession(session_key=session_key)
