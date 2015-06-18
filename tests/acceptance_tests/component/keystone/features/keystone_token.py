#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#
# Copyright 2014 Telefónica Investigación y Desarrollo, S.A.U
#
# This file is part of FI-WARE project.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
#
# You may obtain a copy of the License at:
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#
# See the License for the specific language governing permissions and
# limitations under the License.
#
# For those usages not covered by the Apache version 2.0 License please
# contact with opensource@tid.es
#
__author__ = 'fla'

# -*- coding: utf-8 -*-
from lettuce import step, world, before
from commons.configuration import TENANT_NAME, USERNAME, PASSWORD, KEYSTONE_URL, TOKEN_LENGTH
from expired_users import ExpiredUsers
import requests

@before.each_feature
def setup_feature(feature):

    world.expiredusers = ExpiredUsers(TENANT_NAME, USERNAME, PASSWORD)

@before.each_scenario
def setup(scenario):
    pass

@step(u'a connectivity to the Keystone service')
def set_keystone_service_endpoint(step):

    world.expiredusers.set_keystone_endpoint(KEYSTONE_URL)

    try:
        _ = requests.get(world.expiredusers.get_keystone_endpoint(), timeout=5)
        print("True")
    except requests.ConnectionError:
        assert False, 'Expected True but \n Obtained Connection exception'

@step(u'I request a token to the Keystone')
def get_admin_token(step):

    world.expiredusers.get_admin_token()
    assert world.expiredusers.getadmintoken() is not None, 'Expected not None value \n Obtained None'

@step(u'Given a valid tenantName, username and password')
def given_a_valid_tenantname_username_and_password(step):
    pass

@step(u'the keystone return me a json message with a valid token')
def check_admin_token(step):
    result = world.expiredusers.getadmintoken()

    # We need to validate the token 937ed33c72d74d9492d0e18bf20be599

    assert len(result) == TOKEN_LENGTH, 'Expected a token with length: 32 \n Obtained a token with length: {}'.format(len(retulst))

