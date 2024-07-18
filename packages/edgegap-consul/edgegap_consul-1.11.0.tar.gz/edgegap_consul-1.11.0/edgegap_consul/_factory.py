import os
import re

from ._configuration import ConsulConfiguration
from ._reader import AsyncConsulReader, ConsulReader


class ConsulReaderFactory:
    __consul_pattern__ = r'\[h=(?P<host>[^\]]*),t=(?P<token>[^\]]*)\]'

    def __parse_old_syntax(self) -> ConsulConfiguration | None:
        consul_values = os.environ.get('CONSUL', '[h=localhost,t=None]')

        if isinstance(consul_values, str) and len(consul_values) > 0:
            match = re.match(self.__consul_pattern__, consul_values)

            if match:
                host = match.group('host')
                token = match.group('token')

                return ConsulConfiguration(host=host, token=token)

    def get_configuration(self) -> ConsulConfiguration:
        configuration = self.__parse_old_syntax()

        # implement a new syntax if needed
        # configuration = self.__parse()

        if configuration is None:
            raise ValueError('Could not parse Consul Value, please set environment variables correctly')

        return configuration

    def from_env(self) -> ConsulReader:
        configuration = self.get_configuration()

        return ConsulReader(configuration)

    def async_from_env(self) -> AsyncConsulReader:
        configuration = self.get_configuration()

        return AsyncConsulReader(configuration)
