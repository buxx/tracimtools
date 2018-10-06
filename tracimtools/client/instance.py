# coding: utf-8
from tracimtools.client.urls import Urls



class Instance(object):
    def __init__(
        self, 
        host: str,
        port: int = 80,
        base_path: str = '/api/v2/',
        https: bool = True,
        urls: Urls = None,
    ) -> None:
        self._host = host
        self._port = port
        self._base_path = base_path
        self._https = https
        self._urls = None  # type: Urls
        # TODO BS 2018-10-06: Build url matching tracim version
        self._built_urls()

    def _built_urls(self):
        pass

    @property
    def base_url(self) -> str:
        return '{}{}:{}{}'.format(
            'https://' if self._https else 'http://',
            self._host,
            self._port,
            self._base_path,
        )

    @property
    def urls(self) -> Urls:
        return self._urls

