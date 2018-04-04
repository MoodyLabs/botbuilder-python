# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from botbuilder.core import BotFrameworkAdapter, BotFrameworkAdapterSettings, BotContext
from botbuilder.schema import Activity


class TestBotContext:
    def test_bot_context_should_fail_without_activity_and_adapter(self):
        try:
            context = BotContext(None, None)
        except TypeError:
            pass
        except BaseException as e:
            raise e
        else:
            raise AssertionError("BotContext was created without an adapter and activity.")

    def test_bot_context_should_fail_without_activity(self):
        settings = BotFrameworkAdapterSettings('', '')
        adapter = BotFrameworkAdapter(settings)
        try:
            context = BotContext(adapter, None)
        except TypeError:
            pass
        except BaseException as e:
            raise e
        else:
            raise AssertionError("BotContext was created without an activity.")

    def test_bot_context_should_fail_without_adapter(self):
        activity = Activity()
        try:
            context = BotContext(None, activity)
        except TypeError:
            pass
        except BaseException as e:
            raise e
        else:
            raise AssertionError("BotContext was created without an adapter.")

    def test_bot_context_should_pass_with_activity_and_adapter(self):
        activity = Activity()
        settings = BotFrameworkAdapterSettings('', '')
        adapter = BotFrameworkAdapter(settings)
        try:
            context = BotContext(adapter, activity)
        except TypeError:
            raise AssertionError("BotContext was not created with an adapter and activity.")
        except BaseException as e:
            raise e
        else:
            pass

