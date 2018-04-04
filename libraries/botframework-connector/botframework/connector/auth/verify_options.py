# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

class VerifyOptions:
    def __init__(self, issuer, audience, clock_tolerance, ignore_expiration):
        self.issuer = issuer
        self.audience = audience
        self.clock_tolerance = clock_tolerance
        self.ignore_expiration = ignore_expiration
        