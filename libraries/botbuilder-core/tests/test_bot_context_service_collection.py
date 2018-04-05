# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from typing import Callable
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

    def test_adding_a_duplicate_key_should_fail(self):
        services = BotContextServiceCollection()
        services.add('key', lambda x: x * 1)

        try:
            services.add('key', lambda x: x * 2)
        except ValueError:
            pass
        else:
            raise AssertionError('Should not have added duplicate key.')

    def test_get_services_should_return_dict_with_two_services(self):
        services = BotContextServiceCollection()
        services.add('key', lambda x: x * 1)
        services.add('key_2', lambda x: x)

        callable_services = services.get_services(Callable)
        number_of_services = 0
        for key in callable_services:
            number_of_services += 1

        assert number_of_services == 2

    def test_get_services_should_return_dict_with_no_services(self):
        services = BotContextServiceCollection()
        services.add('key', lambda x: x * 1)
        services.add('key_2', lambda x: x)

        callable_services = services.get_services(int)
        number_of_services = 0
        for key in callable_services:
            number_of_services += 1

        assert number_of_services == 0
