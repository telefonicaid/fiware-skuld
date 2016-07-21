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
from commons import logger_utils
from fiwareskuld.users_management import UserManager
from fiwareskuld.user_resources import UserResources
from commons.configuration import KEYSTONE_URL, TOKEN_LENGTH
import datetime

__author__ = 'fla'


MULTIPLE_CHOICE = 300

logger = logger_utils.get_logger("logs")


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


@given(u'I created several users with values')
def step_create_user(context):
    """
    It creates a set of users according to the data
    introduced in the text
    :param context: Context of the acceptance test execution, with a table with the following data
    # | name | password | role | expired | notified
    :return: nothing
    """

    for user in context.table:
        if len(user) > 3 and user[3] == "True":
            if user[2] == "trial":
                out_date = context.out_trial
            elif user[2] == "community":
                out_date = context.out_community
        elif len(user) > 4 and user[4] == "True":
            if user[2] == "trial":
                out_date = context.out_notified_trial
            elif user[2] == "community":
                out_date = context.out_notified_community
        else:
            out_date = None
        context.user_manager.create_user(user[0], user[1], user[2], out_date)
        context.user_resources = UserResources(user[0], user[1], None, user[0])


@when(u'I request a list of "{role}" users from the Keystone')
@when(u'I request a list of "{role}" users')
@given(u'a list of "{role}" users from the Keystone')
@given(u'a list of "{role}" users')
def step_request_role_users_list(context, role):
    """
    Request the list of role users from the Keystone.
    :param context: Context of the acceptance test execution.
    :param role: the role of the users to get
    :return: Nothing.
    """
    if role == "trial":
        context.list_user = context.expiredusers.get_trial_users()
    elif role == "community":
        context.list_user = context.expiredusers.get_community_users()
    else:
        context.list_user = context.expiredusers.get_users()


@then(u'the component returns a list with "{users}" users')
def step_check_list_trial_users_returned(context, users):
    """
    Request for the list with users selected.
    :param context: Context of the acceptance test execution.
    :param listusers: the number of users
    :return: Nothing.
    """
    assert context.list_user is not None, 'Expected a valid list users'
    assert len(context.list_user) == int(users), \
        'Expected a list of users with {0} length and found {1}'.format(users, len(context.list_user))


@when(u'I request a list of expired "{role}" users')
def step_request_list_trial_expired_users(context, role):
    """
    From the list of trial users, returns the list of expired users.
    :param context: Context of the acceptance test execution.
    :return: Nothing.
    """
    if role == "trial":
        context.expiredusers.expired_users = context.expiredusers.get_list_expired_trial_users()
    elif role == "community":
        context.expiredusers.expired_users = context.expiredusers.get_list_expired_community_users()
    else:
        context.expiredusers = None


@then(u'the component returns a list with "{number}" expired users')
def step_get_list_community_expired_users(context, number):
    """
    Recover the list of expired trial users.
    :param context: Context of the acceptance test execution.
    :return: Nothing.
    """
    try:
        result = context.expiredusers.expired_users
        logger.debug('\n      Number of expired community users found: {}\n\n'.format(len(result)))
        assert result is not None, 'Expected a valid list expired users'
        assert len(result) == int(number), \
            'Expected a list of users with {0} length and found {1}'.format(number, len(result))

    except ValueError:
        assert False, 'Cannot recover the list of community users'


@when(u'I request a list of expired yellow-red "{role}" users')
def step_impl_get_yellow_red_trial(context, role):
    """
    It gets the list of notified and deleted users which are expired.
    :param context: Context of the acceptance test execution.
    :param role: the role
    :return: Nothing.
    """
    if role == "trial":
        context.yellow, context.red = context.expiredusers.get_yellow_red_trial_users()
    elif role == "community":
        context.yellow, context.red = context.expiredusers.get_yellow_red_community_users()
    else:
        context.yellow, context.red = None, None


@then(u'the component returns a list with "{number}" yellow users')
def step_impl_get_yellow(context, number):
    """
    It gets the list of notified users which are expired.
    :param context: Context of the acceptance test execution.
    :param role: the number to be compared
    :return: Nothing.
    """
    assert int(number) == len(context.yellow), 'Expected to find a yellow list ' \
                                               'of {0} length: found {1}'.format(int(number), len(context.yellow))


@then(u'the component returns a list with "{number}" red users')
def step_impl_get_red(context, number):
    """
    It gets the list of deleted users which are expired.
    :param context: Context of the acceptance test execution.
    :param role: the number to be compared
    :return: Nothing.
    """
    assert int(number) == len(context.red), 'Expected to find a yellow list ' \
                                            'of {0} length: found {1}'.format(int(number), len(context.red))


@given(u'a set of resources for the user')
@when(u'a set of resources for the user')
def step_create_resources(context):
    """
    It creates a set of resources for the user, according to the data
    obtained in the context.
    :param context: Context of the acceptance test execution.
    :return: Nothing.
    """

    try:
        image = context.user_resources.glance.get_images()[0].id
        for resource in context.table:
            for i in range(0, int(resource[1])):
                context.user_manager.create_vm_for_user(resource[0], "{0}{1}".format(resource[3], i), image)
            for i in range(0, int(resource[2])):
                context.user_manager.create_secgroup_for_user(resource[0], "{0}{1}".format(resource[3], i))
    except Exception as e:
        print(e)
        context.message = e.message


@when(u'I request for showing resources for user "{user}"')
def step_create_sec_group(context, user):
    """
    It obtains the resources for the user.
    :param context: Context of the acceptance test execution.
    :return: Nothing.
    """
    context.resources = context.user_manager.get_user_resources(user)

@then(u'the component returns a list with "{number1}" security groups and "{number2}" vms for user "{user_id}"')
def step_impl_get_red(context, number1, number2, user_id):
    resources = context.user_manager.get_user_resources(user_id)
    assert int(number1) == len(resources["nsecuritygroups"]),\
        'Expected to find a security groups list of {0} length: found {1}'.format(int(number1),
                                                                                  len(resources["nsecuritygroups"]))
    assert int(number2) == len(resources["vms"]), 'Expected to find a vms list ' \
                                                  'of {0} length: found {1}'.format(int(number2),
                                                                                    len(resources["vms"]))


@then(u'the component return an exception with the message "{message}"')
def step_message_for_wrong_data(context, message):
    """
    Check that the component return the error message.
    :param context: Context of the acceptance test execution.
    :param message: Message to check.
    :return: Nothing.
    """
    result = unicode(context.message)
    assert result == message, message


@when(u'I request for saving expired "{role}" users')
def step_saving_expired_users(context, role):
    """
    It tests the creating of the files for expired users.
    :param context: Context of the acceptance test execution.
    :param role: the role users.
    :return: Nothing.
    """
    if role == "trial":
        context.expiredusers.save_trial_lists(False)
    elif role == "community":
        context.expiredusers.save_community_lists(False)


@then(u'I obtain a file with "{number_notify}" notified users and "{number_delete}" deleted users')
def step_get_expired_users_from_file(context, number_notify, number_delete):
    """
    It check the number of notified and deleted users.
    :param context: Context of the acceptance test execution.
    :param number_notify: the number to check
    :param number_delete: the number to check
    :return: Nothing.
    """

    notify_ids = _get_ids("users_to_notify.txt")
    delete_ids = _get_ids("users_to_delete.txt")
    assert len(notify_ids) == int(number_notify), \
        'Expected a list of notified users with {0} length and found {1}'.format(int(number_notify),
                                                                                 len(notify_ids))
    assert len(delete_ids) == int(number_delete), \
        'Expected a list of deleted users with {0} length and found {1}'.format(int(number_delete),
                                                                                len(delete_ids))


@when(u'I request for deleting expired "{role}" users')
def step_deleting_expired_users(context, role):
    """
    It deletes teh expired users.
    :param context:  Context of the acceptance test execution.
    :param role: the role.
    :return: Nothing.
    """
    if role == "trial":
        context.user_manager.deleting_expired_trial_users_and_resources()
    else:
        print("error")


@then(u'the user "{user}" has role "{role}"')
def step_check_has_role(context, user, role):
    """
    It checks if the user has the right role.
    :param context:  Context of the acceptance test execution.
    :param user: the user
    :param role: the role
    :return: Nothing.
    """
    roles = context.expiredusers.get_roles_user_id(user)
    if "member" in roles:
        roles.remove("member")
    if "owner" in roles:
        roles.remove("owner")
        roles.remove("owner")
    assert roles[0] == role, \
        'Expected a a different roles: Expected {0} and found {1}'.format(role, roles[0])


def _get_ids(file):
    with open(file, 'r') as f:
        data = f.read()
    f.closed

    lines = data.splitlines()
    return lines
