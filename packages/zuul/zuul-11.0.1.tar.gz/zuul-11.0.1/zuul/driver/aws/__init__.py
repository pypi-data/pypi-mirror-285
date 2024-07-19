# Copyright 2024 Acme Gating, LLC
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import urllib

from zuul.driver import Driver, ConnectionInterface, ProviderInterface
from zuul.driver.aws import awsconnection, awsprovider


class AwsDriver(Driver, ConnectionInterface, ProviderInterface):
    name = 'aws'

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.endpoints = {}

    def getConnection(self, name, config):
        return awsconnection.AwsConnection(self, name, config)

    def getProvider(self, connection, canonical_name, provider_config):
        return awsprovider.AwsProvider(
            self, connection, canonical_name, provider_config)

    def getProviderSchema(self):
        return awsprovider.AwsProviderSchema().getProviderSchema()

    def getEndpoint(self, provider):
        # An aws endpoint is a simply a region on the connection
        # (presumably there is exactyl one aws connection, but in case
        # someone uses boto to access as aws-compatible cloud we will
        # also use the connection).
        endpoint_id = '/'.join([
            urllib.parse.quote_plus(provider.connection.connection_name),
            urllib.parse.quote_plus(provider.region),
        ])
        try:
            return self.endpoints[endpoint_id]
        except KeyError:
            pass
        endpoint = awsprovider.AwsProviderEndpoint(
            self, provider.connection, provider.region)
        self.endpoints[endpoint_id] = endpoint
        return endpoint
