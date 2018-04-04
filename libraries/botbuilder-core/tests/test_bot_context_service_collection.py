# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from botbuilder.core import BotContextServiceCollection


class TestBotContextServiceCollection:
    def test_add_service_to_bot_context_service_collection(self):
        services = BotContextServiceCollection()

        try:
            services.add('plus_1', lambda x: x + 1)
        except BaseException as e:
            raise e

    def test_add_and_get_service_from_bot_context_service_collection(self):
        services = BotContextServiceCollection()

        try:
            services.add('plus_1', lambda x: x + 1)

            plus_1 = services.get('plus_1')
            two = plus_1(1)

            assert two == 2
        except BaseException as e:
            raise e

    def test_adding_none_type_key_should_fail(self):
        services = BotContextServiceCollection()

        try:
            services.add(None, lambda x: x + 1)
        except TypeError:
            pass
        else:
            raise AssertionError('Should not have added a None-type key.')

    def test_adding_none_type_service_should_fail(self):
        services = BotContextServiceCollection()

        try:
            services.add('key', None)
        except TypeError:
            pass
        else:
            raise AssertionError('Should not have added a None-type service.')

    def test_get_on_missing_key_should_fail(self):
        services = BotContextServiceCollection()

        try:
            service = services.get('key')
        except KeyError:
            pass
        else:
            raise AssertionError('Should not have successfully retrieved service for missing key.')
