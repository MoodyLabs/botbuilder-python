import asyncio
import json
from datetime import datetime, timedelta
import requests
from jwt.algorithms import RSAAlgorithm
import jwt
from .claims_identity import ClaimsIdentity
from .verify_options import VerifyOptions

class JwtTokenExtractor:
    metadataCache = {}

    def __init__(self, validationParams: VerifyOptions, metadata_url: str, allowedAlgorithms: list, validator=None):
        self.validation_parameters = validationParams
        self.validation_parameters.algorithms = allowedAlgorithms
        self.open_id_metadata = JwtTokenExtractor.get_open_id_metadata(metadata_url)
        self.validator = validator if validator is not None else lambda x: True

    @staticmethod
    def get_open_id_metadata(metadata_url: str):
        metadata = JwtTokenExtractor.metadataCache.get(metadata_url, None)
        if metadata is None:
            metadata = _OpenIdMetadata(metadata_url)
            JwtTokenExtractor.metadataCache.setdefault(metadata_url, metadata)
        return metadata

    async def get_identity_from_auth_header(self, auth_header: str) -> ClaimsIdentity:
        if not auth_header:
            return None
        parts = auth_header.split(" ")
        if len(parts) == 2:
            return await self.get_identity(parts[0], parts[1])
        return None

    async def get_identity(self, schema: str, parameter: str) -> ClaimsIdentity:
        # No header in correct scheme or no token
        if schema != "Bearer" or not parameter:
            return None

        # Issuer isn't allowed? No need to check signature
        if not self._has_allowed_issuer(parameter):
            return None

        try:
            return await self._validate_token(parameter)
        except:
            raise

    def _has_allowed_issuer(self, jwt_token: str) -> bool:
        decoded = jwt.decode(jwt_token, verify=False)
        issuer = decoded.get("iss", None)
        if issuer in self.validation_parameters.issuer:
            return True

        return issuer is self.validation_parameters.issuer

    async def _validate_token(self, jwt_token: str) -> ClaimsIdentity:
        headers = jwt.get_unverified_header(jwt_token)

        # Update the signing tokens from the last refresh
        key_id = headers.get("kid", None)
        metadata = await self.open_id_metadata.get(key_id)


        if headers.get("alg", None) not in self.validation_parameters.algorithms:
            raise Exception('Token signing algorithm not in allowed list')

        if self.validator is not None:
            if not self.validator(metadata.endorsements):
                raise Exception('Could not validate endorsement key')

        options = {
            'verify_aud': False,
            'verify_exp': not self.validation_parameters.ignore_expiration}
        decoded_payload = jwt.decode(jwt_token, metadata.public_key, options=options)
        claims = ClaimsIdentity(decoded_payload, True)

        return claims

class _OpenIdMetadata:
    def __init__(self, url):
        self.url = url
        self.keys = []
        self.last_updated = datetime.min

    async def get(self, key_id: str):
        # If keys are more than 5 days old, refresh them
        if self.last_updated < (datetime.now() + timedelta(days=5)):
            await self._refresh()
        return self._find(key_id)

    async def _refresh(self):
        response = requests.get(self.url)
        response.raise_for_status()
        keys_url = response.json()["jwks_uri"]
        response_keys = requests.get(keys_url)
        response_keys.raise_for_status()
        self.last_updated = datetime.now()
        self.keys = response_keys.json()["keys"]

    def _find(self, key_id: str):
        if not self.keys:
            return None
        key = next(x for x in self.keys if x["kid"] == key_id)
        public_key = RSAAlgorithm.from_jwk(json.dumps(key))
        endorsements = key.get("endorsements", [])
        return _OpenIdConfig(public_key, endorsements)

class _OpenIdConfig:
    def __init__(self, public_key, endorsements):
        self.public_key = public_key
        self.endorsements = endorsements
