# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from typing import Any


class BotContextServiceCollection(object):
    _services = {}

    def get(self, key: str) -> Any:
        if key is None:
            raise TypeError('BotContextServiceCollection.get(): the provided "key" cannot be of type None.')
        try:
            return self._services[key]
        except KeyError:
            raise KeyError(f'BotContextServiceCollection.get(): the key "{key}" was not found.')
        except BaseException as e:
            raise e

    def add(self, key: str, service: Any) -> None:
        if key is None:
            raise TypeError('BotContextServiceCollection.get(): the provided "key" cannot be of type None.')
        if service is None:
            raise TypeError('BotContextServiceCollection.get(): the provided "service" cannot be of type None.')

        try:
            self._services[key] = service
        except BaseException as e:
            raise e
