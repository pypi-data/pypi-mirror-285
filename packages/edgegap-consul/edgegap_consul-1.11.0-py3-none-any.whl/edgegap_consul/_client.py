import asyncio
import warnings

import aiohttp
from consul import base


class AsyncClient(base.HTTPClient):
    """Asyncio adapter for python consul using aiohttp library"""

    def __init__(self, *args, loop=None, **kwargs):
        super().__init__(*args, **kwargs)
        self._loop = loop or asyncio.get_event_loop()
        connector = aiohttp.TCPConnector(
            loop=self._loop,
            verify_ssl=self.verify,
        )
        self._session = aiohttp.ClientSession(connector=connector)

    async def _request(self, callback, method, uri, data=None):
        resp = await self._session.request(method, uri, data=data)
        body = await resp.text(encoding='utf-8')

        if resp.status == 599:
            raise base.Timeout

        r = base.Response(resp.status, resp.headers, body)

        return callback(r)

    def __del__(self):
        if not self._session.closed:
            warnings.warn('Unclosed connector in aio.Consul.HTTPClient', ResourceWarning)
            asyncio.ensure_future(self.close())

    async def get(self, callback, path, params=None):
        uri = self.uri(path, params)

        return await self._request(callback, 'GET', uri)

    async def put(self, callback, path, params=None, data=''):
        uri = self.uri(path, params)

        return await self._request(callback, 'PUT', uri, data=data)

    async def delete(self, callback, path, params=None):
        uri = self.uri(path, params)

        return await self._request(callback, 'DELETE', uri)

    async def post(self, callback, path, params=None, data=''):
        uri = self.uri(path, params)

        return await self._request(callback, 'POST', uri, data=data)

    async def close(self):
        await self._session.close()


class AsyncConsul(base.Consul):
    def __init__(self, *args, loop=None, **kwargs):
        self._loop = loop or asyncio.get_event_loop()
        super().__init__(*args, **kwargs)

    def connect(self, host: str, port: int, scheme: str, verify: bool = True, cert=None):
        return AsyncClient(
            host,
            port,
            scheme,
            loop=self._loop,
            verify=verify,
            cert=None,
        )

    async def close(self):
        await self.http.close()
