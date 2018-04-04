# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from botbuilder.schema import Activity

from .emulator_validation import EmulatorValidation
from .channel_validation import ChannelValidation
from .claims_identity import ClaimsIdentity
from .credential_provider import CredentialProvider
from .microsoft_app_credentials import MicrosoftAppCredentials


class JwtTokenValidation:

    @staticmethod
    async def authenticate_request(activity: Activity, auth_header: str, credentials: CredentialProvider):
        """Validates the security tokens required by the Bot Framework Protocol. Throws on any exceptions.
        
        :param activity: The incoming Activity from the Bot Framework or the Emulator
        :type activity: ~botframework.connector.models.Activity
        :param auth_header: The Bearer token included as part of the request
        :type auth_header: str
        :param credentials: The set of valid credentials, such as the Bot Application ID
        :type credentials: CredentialProvider

        :raises Exception:
        """
        if not auth_header:
            # No auth header was sent. We might be on the anonymous code path.
            is_auth_disabled = await credentials.is_authentication_disabled()
            if is_auth_disabled:
                # We are on the anonymous code path.
                return ClaimsIdentity({}, True)  # Not sure if this should be true or not.

            # No Auth Header. Auth is required. Request is not authorized.
            raise Exception('Unauthorized Access. Request is not authorized')

        claims_identity = await JwtTokenValidation.validate_auth_header(auth_header, credentials, activity.service_url)

        # On the standard Auth path, we need to trust the URL that was incoming.
        MicrosoftAppCredentials.trust_service_url(activity.service_url)

        return claims_identity

    @staticmethod
    async def validate_auth_header(auth_header: str,
                                   credentials: CredentialProvider,
                                   service_url: str) -> ClaimsIdentity:
        if type(auth_header) != str or not auth_header.replace(' ', ''):
            raise TypeError('JwtTokenValidation.validate_auth_header(): Invalid auth_header received.')

        using_emulator: bool = EmulatorValidation.is_token_from_emulator(auth_header)

        if using_emulator:
            return await EmulatorValidation.authenticate_emulator_token(auth_header, credentials)
        else:
            if service_url is not None:
                return await ChannelValidation.authenticate_token_service_url(auth_header, credentials, service_url)
            else:
                return await ChannelValidation.authenticate_token(auth_header, credentials)
