# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from typing import Any, Dict


class BotContextServiceCollection(object):
    """
    Represents a set of collection of services associated with the BotContext.
    """

    def __init__(self):
        self._services = {}

    def get(self, key: str) -> Any:
        """
        Get a service by its key.
        :param key:
        :return:
        """
        if key is None:
            raise TypeError('BotContextServiceCollection.get(): the provided "key" cannot be of type None.')
        try:
            return self._services[key]
        except KeyError:
            raise KeyError(f'BotContextServiceCollection.get(): the key "{key}" was not found.')
        except BaseException as e:
            raise e

    def add(self, key: str, service: Any) -> None:
        """
        Add a service with a specified key.
        :param key:
        :param service:
        :return:
        """
        if key is None:
            raise TypeError('BotContextServiceCollection.get(): the provided "key" cannot be of type None.')
        if service is None:
            raise TypeError('BotContextServiceCollection.get(): the provided "service" cannot be of type None.')
        if key in self._services:
            raise ValueError(f'A service is already registered with the specified key: "{key}".')
        try:
            self._services[key] = service
        except BaseException as e:
            raise e

    def get_services(self, type: Any) -> Dict[str, Any]:
        """
        Returns all entries in the collection of a specified type.
        :param type:
        :return:
        """
        mapping = {}
        for key in self._services:
            if isinstance(self._services[key], type):
                mapping[key] = self._services[key]

        return mapping
