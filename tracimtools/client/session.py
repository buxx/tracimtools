# condig: utf-8
import aiohttp


class Session(object):
    @property
    def request_kwargs(self) -> dict:
        raise notImplementedError()


class BasicAuthSession(object):
    def __init__(self, login: str, password) -> None:
        self._login = login
        self._password = password

    @property
    def request_kwargs(self) -> dict:
        return {
            'auth': aiohttp.BasicAuth(login=self._login, password=self._password),
        }


class CookieSession(object):
    def __init__(self, session_key: str) -> None:
        self._session_key = session_key

    def session_key(self) -> str:
        return self._session_key

    @property
    def request_kwargs(self) -> dict:
        raise notImplementedError('TODO')
