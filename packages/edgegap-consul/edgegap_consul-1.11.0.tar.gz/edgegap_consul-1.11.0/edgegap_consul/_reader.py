import logging

import consul.aio

from ._client import AsyncConsul
from ._configuration import ConsulConfiguration

logger = logging.getLogger('edgegap-consul.Reader')


class ConsulReader:
    def __init__(self, configuration: ConsulConfiguration):
        self._configuration = configuration
        self._client = consul.Consul(**self._configuration.model_dump())

    @staticmethod
    def _parse(data: dict) -> tuple[bool, [str | None]]:
        value = None
        key_exists = False

        if isinstance(data, dict):
            value = data.get('Value')

            if isinstance(value, bytes):
                value = str(value, 'utf-8')

            key_exists = True

        return key_exists, value

    def get(self, key: str) -> tuple[bool, [str | None]]:
        try:
            _, data = self._client.kv.get(key)

            return self._parse(data)

        except ConnectionError as e:
            logger.exception(f'Failed to get [{key}]: {e}')

    def check(self) -> bool:
        status = self._client.status.leader()

        return isinstance(status, str)


class AsyncConsulReader(ConsulReader):
    def __init__(self, configuration: ConsulConfiguration):
        super().__init__(configuration)
        self._client = AsyncConsul(**self._configuration.model_dump())

    async def get(self, key: str) -> tuple[bool, [str | None]]:
        try:
            _, data = await self._client.kv.get(key)

            return self._parse(data)

        except ConnectionError as e:
            logger.exception(f'Failed to get [{key}]: {e}')
        finally:
            await self._client.close()
