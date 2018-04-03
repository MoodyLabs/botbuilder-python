# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from abc import ABC, abstractmethod
from typing import List, Callable
from botbuilder.schema import Activity, ConversationReference

from .bot_context import BotContext
from .middleware_set import MiddlewareSet


class BotAdapter(ABC):
    def __init__(self):
        self._middleware = MiddlewareSet()

    @abstractmethod
    async def send_activities(self, context: BotContext, activities: List[Activity]):
        raise NotImplementedError()

    @abstractmethod
    async def update_activity(self, context: BotContext, activity: Activity):
        raise NotImplementedError()

    @abstractmethod
    async def delete_activity(self, context: BotContext, reference: ConversationReference):
        raise NotImplementedError()

    def use(self, middleware):
        self._middleware.use(middleware)

    async def run_pipeline(self, context: BotContext, callback: Callable=None):
        if callable(callback):
            if context.activity:
                return await self._middleware.receive_activity_with_status(context, callback)

    async def create_conversation(self, channel_id: str, callback: Callable[[BotContext, Callable], None]):
        raise NotImplementedError()

    async def continue_conversation(self, reference: ConversationReference,
                                    callback: Callable[[BotContext, Callable], None]):
        raise NotImplementedError()