# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import asyncio
from typing import List, Callable, Dict
from botbuilder.schema import Activity, ConversationReference
from botframework.connector import ConnectorClient
from botframework.connector.auth import (ClaimsIdentity, MicrosoftAppCredentials,
                                         JwtTokenValidation, SimpleCredentialProvider,
                                         Constants as AuthenticationConstants)

from .bot_adapter import BotAdapter
from .bot_context import BotContext


class BotFrameworkAdapterSettings(object):
    def __init__(self, app_id: str, app_password: str):
        self.app_id = app_id
        self.app_password = app_password


class BotFrameworkAdapter(BotAdapter):

    def __init__(self, settings: BotFrameworkAdapterSettings):
        super(BotFrameworkAdapter, self).__init__()
        if settings is None:
            raise TypeError('BotFrameworkAdapter(): A BotFrameworkAdapter cannot be instantiated without '
                            'the "settings" parameter.')
        self.settings = settings or BotFrameworkAdapterSettings('', '')
        self._credentials = MicrosoftAppCredentials(self.settings.app_id, self.settings.app_password)
        self._credential_provider = SimpleCredentialProvider(self.settings.app_id, self.settings.app_password)
        self.app_credential_map: Dict[str, MicrosoftAppCredentials] = {}

    async def process_activity(self, req, auth_header: str, logic: Callable):
        """
        Creates a turn context and runs the middleware pipeline for an incoming activity.
        :param req:
        :param auth_header:
        :param logic:
        :return:
        """
        request = self.parse_request(req)
        auth_header = auth_header or ''

        claims_identity = await JwtTokenValidation.authenticate_request(request,
                                                                        auth_header,
                                                                        self._credential_provider)

        context = BotContext(self, request)
        # context.services.add("bot_identity", claims_identity)
        # connector_client = await self.create_connector_client_async(request.service_url, claims_identity)
        # context.services.add("connector_client", connector_client)
        return await self.run_pipeline(context, logic)

    async def authenticate_request(self, request: Activity, auth_header: str):
        await JwtTokenValidation.authenticate_request(request, auth_header, self._credential_provider)

    # async def continue_conversation(self,
    #                                 bot_app_id: str,
    #                                 reference: ConversationReference,
    #                                 callback: Callable[[BotContext, Callable], None]):
    #     raise NotImplementedError()

    async def create_connector_client_async(self, service_url: str, claims_identity: ClaimsIdentity):
        """
        Asynchronously creates the connector client.
        :param service_url:
        :param claims_identity:
        :return:
        """
        if claims_identity is None:
            raise TypeError("claims_identity cannot be None. Pass an anonymous ClaimsIdentity if authentication "
                            "is turned off.")

        bot_app_id_claim = BotFrameworkAdapter.get_bot_app_id_claim(claims_identity)

        if bot_app_id_claim is not None:
            bot_id = bot_app_id_claim.value
            app_credentials = await self.get_app_credentials_async(bot_id)
            return self.create_connector_client(service_url, app_credentials)

    @staticmethod
    def get_bot_app_id_claim(claims_identity: ClaimsIdentity):
        """
        Returns a valid claims identity.
        :param claims_identity:
        :return:
        """
        for key, claim in claims_identity.claims.items():
            if claim.type == AuthenticationConstants.AUDIENCE_CLAIM:
                return claim
            if claim.type == AuthenticationConstants.APP_ID_CLAIM:
                return claim

    def create_connector_client(self, service_url: str, app_credentials: MicrosoftAppCredentials=None):
        """
        Creates the connector client.
        :param service_url:
        :param app_credentials:
        :return:
        """
        if app_credentials is not None:
            return ConnectorClient(app_credentials, service_url)
        else:
            credentials = MicrosoftAppCredentials('', '')
            return ConnectorClient(credentials, service_url)

    async def get_app_credentials_async(self, app_id: str):
        """
        Gets the application credentials. App Credentials are cached so as to ensure
        we are not refreshing token every time.
        :param app_id:
        :return:
        """
        if not app_id.replace(' ', ''):
            return MicrosoftAppCredentials('', '')
        try:
            if app_id in self.app_credential_map:
                app_credentials = self.app_credential_map[app_id]
            else:
                app_password = await self._credential_provider.get_app_password(app_id)
                app_credentials = MicrosoftAppCredentials(app_id, app_password)
                self.app_credential_map[app_id] = app_credentials
        except BaseException as e:
            raise e
        else:
            return app_credentials

    @staticmethod
    def parse_request(req):  # Why on earth is this asynchronous?
        """
        Parses and validates request
        :param req:
        :return:
        """

        def validate_activity(activity: Activity):
            if not isinstance(activity.type, str):
                raise TypeError('BotFrameworkAdapter.parse_request(): invalid or missing activity type.')
            return True

        if not isinstance(req, Activity):
            # If the req is a raw HTTP Request, try to deserialize it into an Activity and return the Activity.
            if hasattr(req, 'body'):
                try:
                    activity = Activity().deserialize(req.body)
                    is_valid_activity = validate_activity(activity)
                    if is_valid_activity:
                        return activity
                except BaseException as e:
                    raise e
            elif 'body' in req:
                try:
                    activity = Activity().deserialize(req['body'])
                    is_valid_activity = validate_activity(activity)
                    if is_valid_activity:
                        return activity
                except BaseException as e:
                    raise e
            else:
                raise TypeError('BotFrameworkAdapter.parse_request(): received invalid activity')
        else:
            # The `req` has already been deserialized to an Activity, so verify the Activity.type and return it.
            is_valid_activity = validate_activity(req)
            if is_valid_activity:
                return req

    async def update_activity(self, context: BotContext, activity: Activity):
        try:
            connector_client = ConnectorClient(self._credentials, activity.service_url)
            return connector_client.conversations.update_activity(
                activity.conversation.id,
                activity.conversation.activity_id,
                activity)
        except BaseException as e:
            raise e

    async def delete_activity(self, context: BotContext, conversation_reference: ConversationReference):
        try:
            connector_client = ConnectorClient(self._credentials, conversation_reference.service_url)
            connector_client.conversations.delete_activity(conversation_reference.conversation.id,
                                                           conversation_reference.activity_id)
        except BaseException as e:
            raise e

    async def send_activities(self, context: BotContext, activities: List[Activity]):
        try:
            for activity in activities:
                if activity.type == 'delay':
                    try:
                        delay_in_ms = float(activity.value) / 1000
                    except TypeError:
                        raise TypeError('Unexpected delay value passed. Expected number or str type.')
                    except AttributeError:
                        raise Exception('activity.value was not found.')
                    else:
                        await asyncio.sleep(delay_in_ms)
                else:
                    connector_client = ConnectorClient(self._credentials, activity.service_url)
                    # connector_client = context.services.get("connector_client")
                    responses = await connector_client.conversations.send_to_conversation_async(activity.conversation.id, activity)
        except BaseException as e:
            raise e

    # Legacy code.
    async def send(self, activities: List[Activity]):
        for activity in activities:
            connector = ConnectorClient(self._credentials, base_url=activity.service_url)
            await connector.conversations.send_to_conversation_async(activity.conversation.id, activity)

    async def receive(self, auth_header: str, activity: Activity):
        try:
            await JwtTokenValidation.authenticate_request(activity, auth_header, self._credential_provider)
        except BaseException as e:
            raise e
        else:
            if self.on_receive is not None:
                await self.on_receive(activity)
