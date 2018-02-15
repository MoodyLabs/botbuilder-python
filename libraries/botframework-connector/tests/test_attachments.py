# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#
# Code generated by Microsoft (R) AutoRest Code Generator.
# Changes may cause incorrect behavior and will be lost if the code is
# regenerated.
# --------------------------------------------------------------------------
import os
import base64
import pytest
from azure_devtools.scenario_tests import ReplayableTest

import msrest
from microsoft.botbuilder.schema import *
from microsoft.botframework.connector import ConnectorClient
from microsoft.botframework.connector.auth import MicrosoftAppCredentials

from .authentication_stub import MicrosoftTokenAuthenticationStub

SERVICE_URL = 'https://slack.botframework.com'
CHANNEL_ID = 'slack'
BOT_NAME = 'botbuilder-pc-bot'
BOT_ID = 'B21UTEF8S:T03CWQ0QB'
RECIPIENT_ID = 'U19KH8EHJ:T03CWQ0QB'
CONVERSATION_ID = 'B21UTEF8S:T03CWQ0QB:D2369CT7C'

def get_auth_token():
    try:
        # import app_creds_real
        # Define a "app_creds_real.py" file with your bot credentials as follows:
        # MICROSOFT_APP_ID = '...'
        # MICROSOFT_APP_PASSWORD = '...'
        return MicrosoftAppCredentials(
            'be5a8c67-75dd-424a-b7da-746141e11f7f',
            'poR3ZiMgA3JSUkFOcSjtUGp').get_accessToken()
    except ImportError:
        return 'STUB_ACCESS_TOKEN'

def read_base64(path_to_file):
    path_to_current_file = os.path.realpath(__file__)
    current_directory = os.path.dirname(path_to_current_file)
    path_to_file = os.path.join(current_directory, "resources", path_to_file)

    with open(path_to_file, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
        return encoded_string

auth_token = get_auth_token()

class AttachmentsTest(ReplayableTest):
    def __init__(self, method_name):
        super(AttachmentsTest, self).__init__(method_name)

    @property
    def credentials(self):
        return MicrosoftTokenAuthenticationStub(auth_token)

    def test_attachments_upload_and_get_attachment(self):
        attachment = AttachmentData(
            type='image/png',
            name='Bot.png',
            original_base64=read_base64('bot.png'),
            thumbnail_base64=read_base64('bot_icon.png'))

        connector = ConnectorClient(self.credentials, base_url=SERVICE_URL)
        response = connector.conversations.upload_attachment(CONVERSATION_ID, attachment)
        attachment_id = response.id
        attachment_info = connector.attachments.get_attachment_info(attachment_id)

        assert attachment_info is not None
        assert attachment_info.name == 'Bot.png'
        assert attachment_info.type == 'image/png'
        assert len(attachment_info.views) == 2

    def test_attachments_get_info_invalid_attachment_id_fails(self):
        with pytest.raises(ErrorResponseException) as excinfo:
            connector = ConnectorClient(self.credentials, base_url=SERVICE_URL)
            connector.attachments.get_attachment_info('bt13796-GJS4yaxDLI')

        assert ('Not Found' in str(excinfo.value))

    def test_attachments_get_attachment_view(self):
        original = read_base64('bot.png')
        attachment = AttachmentData(
            type='image/png',
            name='Bot.png',
            original_base64=original,
            thumbnail_base64=read_base64('bot_icon.png'))

        connector = ConnectorClient(self.credentials, base_url=SERVICE_URL)
        response = connector.conversations.upload_attachment(CONVERSATION_ID, attachment)
        attachment_id = response.id
        attachment_stream = connector.attachments.get_attachment(attachment_id, 'original')

        assert len(original) == sum(len(_) for _ in attachment_stream)

    def test_attachments_get_attachment_view_with_invalid_attachment_id_fails(self):
        with pytest.raises(msrest.exceptions.HttpOperationError) as excinfo:
            connector = ConnectorClient(self.credentials, base_url=SERVICE_URL)
            connector.attachments.get_attachment('bt13796-GJS4yaxDLI', 'original')

        assert ('Not Found' in str(excinfo.value))

    def test_attachments_get_attachment_view_with_invalid_view_id_fails(self):
        original = read_base64('bot.png')
        attachment = AttachmentData(
            type='image/png',
            name='Bot.png',
            original_base64=original,
            thumbnail_base64=read_base64('bot_icon.png'))

        with pytest.raises(msrest.exceptions.HttpOperationError) as excinfo:
            connector = ConnectorClient(self.credentials, base_url=SERVICE_URL)
            response = connector.conversations.upload_attachment(CONVERSATION_ID, attachment)
            attachment_id = response.id
            attachment_view = connector.attachments.get_attachment(attachment_id, 'invalid')

        assert ('not found' in str(excinfo.value))
