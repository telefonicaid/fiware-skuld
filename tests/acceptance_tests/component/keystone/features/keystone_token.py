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
from commons.configuration import TENANT_NAME, FAKE_TENANT_NAME
from commons.configuration import USERNAME, PASSWORD, KEYSTONE_URL, TOKEN_LENGTH
from expired_users import ExpiredUsers
import requests

@before.each_feature
def setup_feature(feature):

    world.expiredusers = ExpiredUsers(TENANT_NAME, USERNAME, PASSWORD)

@before.each_scenario
def setup(scenario):
    world.expiredusers.finalList = []
    world.expiredusers.listUsers = []
    world.expiredusers.token = None

@step(u'a connectivity to the Keystone service')
def set_keystone_service_endpoint(step):

    world.expiredusers.set_keystone_endpoint(KEYSTONE_URL)

    try:
        _ = requests.get(world.expiredusers.get_keystone_endpoint(), timeout=5)
        print("True")
    except requests.ConnectionError:
        assert False, 'Expected True but \n Obtained Connection exception'

@step(u'a valid token from the Keystone')
def get_admin_token(step):

    world.message = ''

    try:
        world.expiredusers.get_admin_token()
    except Exception as e:
        world.message = 'The request you have made requires authentication.'

@step(u'a valid tenantName, username and password')
def given_a_valid_tenantname_username_and_password(step):
    pass

@step(u'the keystone return me a json message with a valid token')
def check_admin_token(step):
    result = world.expiredusers.getadmintoken()

    assert len(result) == TOKEN_LENGTH, 'Expected a token with length: 32 ' \
                                        '\n Obtained a token with length: {}'.format(len(result))

@step(u'a list of trial users from the Keystone')
def when_i_request_a_list_of_trial_users_from_the_keystone(step):
    world.expiredusers.get_list_trial_users()

@step(u'the Keystone returns a list with all the trial users registered')
def then_the_keystone_returns_a_list_with_all_the_trial_users_registered(step):

    try:
        result = world.expiredusers.gerlisttrialusers()

        print
        print('      Number of trial users found: {}\n'.format(len(result)))
        print
    except ValueError:
        assert False, 'Cannot recover the list of trial users'


@step(u'I request a list of expired users')
def when_i_request_a_list_of_expired_users(step):
    world.expiredusers.get_list_expired_users()

@step(u'the component returns a list with all the expired trial users')
def then_the_component_returns_a_list_with_all_the_expired_trial_users(step):
    try:
        result = world.expiredusers.gerlisttrialusers()
        print
        print('      Number of expired trial users found: {}\n'.format(len(result)))
        print
    except ValueError:
        assert False, 'Cannot recover the list of trial users'

@step(u'a wrong "([^"]*)", "([^"]*)" and "([^"]*)"')
def given_a_wrong_tenant_username_and_password(step, tenantname, username, password):
    world.expiredusers = ExpiredUsers(tenantname, username, password)

@step(u'the component return an exception with the message "([^"]*)"')
def then_the_component_return_an_exception_with_the_message_group1(step, group1):
    assert world.message == 'The request you have made requires authentication.'
