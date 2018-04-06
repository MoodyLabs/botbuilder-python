# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from botbuilder.core import BotFrameworkAdapter, BotFrameworkAdapterSettings


class TestBotFrameworkAdapter(object):
    def test_creating_bot_framework_adapter_without_settings_should_throw_an_error(self):
        try:
            adapter = BotFrameworkAdapter(None)
        except TypeError:
            pass
        except BaseException as e:
            raise e
        else:
            raise AssertionError("Should not have created adapter without BotFrameworkAdapterSettings.")

    def test_creating_bot_framework_adapter_with_settings(self):
        try:
            settings = BotFrameworkAdapterSettings('', '')
            adapter = BotFrameworkAdapter(settings)
        except BaseException as e:
            raise e
        else:
            pass

    def test_create_connector_client_without_app_credentials(self):
        settings = BotFrameworkAdapterSettings('', '')
        adapter = BotFrameworkAdapter(settings)

        client = adapter.create_connector_client('http://localhost')
        assert client is not None

    def test_create_connector_client_with_app_credentials(self):
        settings = BotFrameworkAdapterSettings('', '')
        adapter = BotFrameworkAdapter(settings)

        client = adapter.create_connector_client('http://localhost', settings)
        assert client is not None
