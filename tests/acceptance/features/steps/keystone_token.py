#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#
# Copyright 2015 Telefónica Investigación y Desarrollo, S.A.U
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
# -*- coding: utf-8 -*-
import requests
from behave import when, then, given
from skuld.expired_users import ExpiredUsers
from tests.acceptance.commons.configuration import KEYSTONE_URL, TOKEN_LENGTH

__author__ = 'fla'


MULTIPLE_CHOICE = 300


@given(u'a valid tenantName, username and password')
def step_impl(context):
    pass


@given(u'a connectivity to the Keystone service')
def step_impl(context):
    context.expiredusers.set_keystone_endpoint(KEYSTONE_URL)

    try:
        result = requests.get(context.expiredusers.get_keystone_endpoint(), timeout=5)
    except requests.ConnectionError:
        assert False, 'Expected True but \n Obtained Connection exception'

    assert result.status_code == MULTIPLE_CHOICE, 'Expected 300 - Multiple Choice ' \
                                                  'but obtained {}'.format(result.status_code)


@when(u'I request a valid token from the Keystone')
def step_impl(context):
    context.message = ''

    try:
        context.expiredusers.get_admin_token()
    except Exception as inst:
        context.message = 'The request you have made requires authentication.'


@then(u'the keystone return me a json message with a valid token')
def step_impl(context):
    result = context.expiredusers.getadmintoken()

    assert result is not None, 'Expected a valid token but obtained no token'
    assert len(result) == TOKEN_LENGTH, 'Expected a token with length: 32 ' \
                                        '\n Obtained a token with length: {}'.format(len(result))


@given(u'a valid token from the Keystone')
def step_impl(context):
    context.message = ''

    try:
        context.expiredusers.get_admin_token()
    except ValueError:
        context.message = 'The request you have made requires authentication.'


@when(u'I request a list of trial users from the Keystone')
@given(u'a list of trial users from the Keystone')
def step_impl(context):
    context.expiredusers.get_list_trial_users()


@then(u'the Keystone returns a list with all the trial users registered')
def step_impl(context):
    try:
        result = context.expiredusers.gerlisttrialusers()

        print
        print('      Number of trial users found: {}\n'.format(len(result)))
        print
    except ValueError:
        assert False, 'Cannot recover the list of trial users'


@when(u'I request a list of expired users')
def step_impl(context):
    context.expiredusers.get_list_expired_users()


@then(u'the component returns a list with all the expired trial users')
def step_impl(context):
    try:
        result = context.expiredusers.gerlisttrialusers()
        print
        print('      Number of expired trial users found: {}\n'.format(len(result)))
        print
    except ValueError:
        assert False, 'Cannot recover the list of trial users'


@given(u'a wrong "{tenantname}", "{username}" and "{password}"')
def given_a_wrong_tenant_username_and_password(context, tenantname, username, password):
    context.expiredusers = ExpiredUsers(tenantname, username, password)


@then(u'the component return an exception with the message "{message}"')
def step_impl(context, message):
    result = unicode(context.message)
    assert result == message, message
