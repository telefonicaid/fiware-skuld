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
from fiwareskuld.expired_users import ExpiredUsers
from fiwareskuld.create_users import CreateUser
from commons.configuration import KEYSTONE_URL, TOKEN_LENGTH

__author__ = 'fla'


MULTIPLE_CHOICE = 300


@given(u'a valid tenantName, username and password')
def step_valid_data(context):
    """
    Just starting point.
    :param context: Context of the acceptance test execution.
    :return: Nothing.
    """
    pass


@given(u'a connectivity to the Keystone service')
def step_check_connectivity_to_keystone(context):
    """
    Check if we can contact with the Keystone service defined in the KEYSTONE_URL.
    :param context: Context of the acceptance test execution.
    :return: Nothing.
    """
    context.expiredusers.set_keystone_endpoint(KEYSTONE_URL)

    try:
        result = requests.get(context.expiredusers.get_keystone_endpoint(), timeout=5)
    except requests.ConnectionError:
        assert False, 'Expected True but \n Obtained Connection exception'

    assert result.status_code == MULTIPLE_CHOICE, 'Expected 300 - Multiple Choice ' \
                                                  'but obtained {}'.format(result.status_code)


@when(u'I request a valid token from the Keystone')
@given(u'a valid token from the Keystone')
def step_get_valid_token(context):
    """
    Request a valid administration token from the Keystone service.
    :param context: Context of the acceptance test execution.
    :return: Nothing.
    """
    context.message = ''

    try:
        context.expiredusers.get_admin_token()
    except Exception as inst:
        context.message = 'The request you have made requires authentication.'


@then(u'the keystone return me a json message with a valid token')
def step_check_returned_token(context):
    """
    Return the valid token corresponding to an administrator user.
    :param context: Context of the acceptance test execution.
    :return: Noting.
    """
    result = context.expiredusers.getadmintoken()

    assert result is not None, 'Expected a valid token but obtained no token'
    assert len(result) == TOKEN_LENGTH, 'Expected a token with length: 32 ' \
                                        '\n Obtained a token with length: {}'.format(len(result))


@then(u'the Keystone returns a list with trial "{listusers}" users')
def step_check_list_users_returned(context, listusers):
    list_qa_users = context.expiredusers.get_trial_users()
    assert list_qa_users is not None, 'Expected a valid list users but obtained no token'
    assert len(list_qa_users) == int(listusers), \
        'Expected a list of users with {0} length and found {1}'.format(listusers, len(list_qa_users))


@then(u'the Keystone returns a list with community "{listcommunity}" users')
def step_check_list_users_returned(context, listcommunity):
    list_qa_users = context.expiredusers.get_community_users()
    assert list_qa_users is not None, 'Expected a valid list users but obtained no token'
    assert len(list_qa_users) == int(listcommunity), \
        'Expected a list of users with {0} length and found {1}'.format(listcommunity, len(list_qa_users))


@when(u'I request a list of trial users from the Keystone')
@given(u'a list of trial users from the Keystone')
def step_request_trial_users_list(context):
    """
    Request the list of trial users from the Keystone.
    :param context: Context of the acceptance test execution.
    :return: Nothing.
    """
    context.expiredusers.get_trial_users()


@when(u'I request a list of community users from the Keystone')
@given(u'a list of community users from the Keystone')
def step_request_community_users_list(context):
    """
    Request the list of trial users from the Keystone.
    :param context: Context of the acceptance test execution.
    :return: Nothing.
    """
    users = context.expiredusers.get_community_users()
    print('\n      Number of community users found: {}\n\n'.format(len(users)))
    return users


@when(u'a user with name "{username}", password "{password}" and role "{role}" is created')
@given(u'a user with name "{username}", password "{password}" and role "{role}"')
def step_create_user(context, username, password, role):
    try:
        user = context.createusermanagement.create_user(username, password, role)
    except Exception as e:
        print("bad user")
        print ("ERRRRRROR")
        print(e)
        context.message = e.message
        assert False, 'Error to create the user {0}'.format(e.message)


@when(u'an expired user with name "{username}", password "{password}" and role "{role}" is created')
@given(u'an expired user with name "{username}", password "{password}" and role "{role}"')
def step_create_expired_user(context, username, password, role):
    print ("create expired")
    try:
        if role == "trial":
            out_date = context.out_trial
        elif role == "community":
            out_date = context.out_community
        else:
            out_date = None
        print(out_date)
        user = context.createusermanagement.create_user(username, password, role, out_date)
    except Exception as e:
        context.message = e.message
        assert False, 'Error to create the user {0}'.format(e.message)


@then(u'the Keystone returns a list with all the trial users registered')
def step_get_list_trial_users(context):
    """
    Returns the list of the expired users.
    :param context: Context of the acceptance test execution.
    :return: Nothing.
    """
    try:
        result = context.expiredusers.get_trial_users()
        print('\n      Number of trial users found: {}\n\n'.format(len(result)))
    except ValueError:
        assert False, 'Cannot recover the list of trial users'


@when(u'I request a list of expired trial users')
def step_request_list_expired_users(context):
    """
    From the list of trial users, returns the list of expired users.
    :param context: Context of the acceptance test execution.
    :return: Nothing.
    """
    result = context.expiredusers.get_list_expired_trial_users()
    print ("in the result")
    print(result)
    context.expiredusers.finalTrialList = result
    print (context.expiredusers.finalTrialList)


@then(u'the component returns a list with "{number}" expired trial users')
def step_get_list_expired_users(context, number):
    """
    Recover the list of expired trial users.
    :param context: Context of the acceptance test execution.
    :return: Nothing.
    """
    try:
        result = context.expiredusers.finalTrialList

        print('\n      Number of expired trial users found: {}\n\n'.format(len(result)))
        assert result is not None, \
            'Expected a valid list expired users'
        assert len(result) == int(number), \
            'Expected a list of users with {0} length and found {1}'.format(number, len(result))

    except ValueError:
        assert False, 'Cannot recover the list of trial users'


@when(u'I request a list of expired community users')
def step_request_list_expired_users(context):
    """
    From the list of trial users, returns the list of expired users.
    :param context: Context of the acceptance test execution.
    :return: Nothing.
    """
    context.expiredusers.finalCommunityList = context.expiredusers.get_list_expired_community_users()


@then(u'the component returns a list with "{number}" expired community users')
def step_get_list_expired_users(context, number):
    """
    Recover the list of expired trial users.
    :param context: Context of the acceptance test execution.
    :return: Nothing.
    """
    try:
        result = context.expiredusers.finalCommunityList
        print('\n      Number of expired community users found: {}\n\n'.format(len(result)))
        assert result is not None, 'Expected a valid list expired users'
        assert len(result) == int(number), \
            'Expected a list of users with {0} length and found {1}'.format(number, len(result))

    except ValueError:
        assert False, 'Cannot recover the list of community users'


@given(u'a wrong "{tenantname}", "{username}" or "{password}"')
def given_a_wrong_tenant_username_and_password(context, tenantname, username, password):
    """
    Check that the operation to recover trial users with wrong data produce an exception.
    :param context: Context of the acceptance test execution.
    :param tenantname: Wrong tenant name.
    :param username: Wrong user name.
    :param password: Wrong password.
    :return:
    """
    context.expiredusers = ExpiredUsers(tenantname, username, password)


@then(u'the component return an exception with the message "{message}"')
def step_message_for_wrong_data(context, message):
    """
    Check that the component return the error message.
    :param context: Context of the acceptance test execution.
    :param message: Message to check.
    :return:
    """
    result = unicode(context.message)
    assert result == message, message
