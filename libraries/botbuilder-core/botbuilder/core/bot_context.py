# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import asyncio
import sys
from copy import deepcopy, copy
from uuid import uuid4
from typing import List, Callable, Iterable, Tuple
from botbuilder.schema import Activity, ActivityTypes, ConversationReference, ResourceResponse

from .bot_context_service_collection import BotContextServiceCollection
# from .bot_adapter import BotAdapter


class BotContext(object):
    def __init__(self, adapter, activity: Activity):
        if not activity:
            raise TypeError('BotContext must be instantiated with a activity parameter of type Activity.')
        if not adapter:
            raise TypeError('BotContext must be instantiated with an adapter.')

        self.adapter = adapter
        self.activity: Activity = activity
        self.responses: List[Activity] = []
        self.services: BotContextServiceCollection = BotContextServiceCollection()
        self._responded: bool = False
        self._on_send_activity: Callable[[]] = []
        self._on_update_activity: Callable[[]] = []
        self._on_delete_activity: Callable[[]] = []

    async def send_activity(self, *activity_or_text: Tuple[Activity, str]):
        reference = BotContext.get_conversation_reference(self.activity)
        output = [BotContext.apply_conversation_reference(
            Activity(text=a, type='message') if isinstance(a, str) else a, reference)
            for a in activity_or_text]

        async def callback(context: 'BotContext', output):
            responses = await context.adapter.send_activities(context, output)
            context._responded = True
            return responses

        await self._emit(self._on_send_activity, output, callback(self, output))

    async def update_activity(self, activity: Activity):
        return asyncio.ensure_future(self._emit(self._on_update_activity,
                                                activity,
                                                self.adapter.update_activity(activity)))

    @staticmethod
    async def _emit(plugins, arg, logic):
        handlers = copy(plugins)

        async def emit_next(i: int):
            try:
                if i < len(handlers):
                    await handlers[i](arg, emit_next(i + 1))
                asyncio.ensure_future(logic)
            except BaseException as e:
                raise e
        await emit_next(0)

    @staticmethod
    def get_conversation_reference(activity: Activity) -> ConversationReference:
        """
        Returns the conversation reference for an activity. This can be saved as a plain old JSON
        bject and then later used to message the user proactively.

        Usage Example:
        reference = BotContext.get_conversation_reference(context.activity)
        :param activity:
        :return:
        """
        return ConversationReference(activity_id=activity.id,
                                     user=copy(activity.from_property),
                                     bot=copy(activity.recipient),
                                     conversation=copy(activity.conversation),
                                     channel_id=activity.channel_id,
                                     service_url=activity.service_url)

    @staticmethod
    def apply_conversation_reference(activity: Activity,
                                     reference: ConversationReference,
                                     is_incoming: bool=False) -> Activity:
        """
        Updates an activity with the delivery information from a conversation reference. Calling
        this after get_conversation_reference on an incoming activity
        will properly address the reply to a received activity.
        :param activity:
        :param reference:
        :param is_incoming:
        :return:
        """
        activity.channel_id=reference.channel_id
        activity.service_url=reference.service_url
        activity.conversation=reference.conversation
        if is_incoming:
            activity.from_property = reference.user
            activity.recipient = reference.bot
            if reference.activity_id:
                activity.id = reference.activity_id
        else:
            activity.from_property = reference.bot
            activity.recipient = reference.user
            if reference.activity_id:
                activity.reply_to_id = reference.activity_id

        return activity

