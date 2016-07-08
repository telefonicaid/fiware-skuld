#!/usr/bin/env python
# -- encoding: utf-8 --
#
# Copyright 2015 Telefónica Investigación y Desarrollo, S.A.U
#
# This file is part of FI-Core project.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
#
# You may obtain a copy of the License at:
#
# http://www.apache.org/licenses/LICENSE-2.0
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
from fiwareskuld.conf import settings
from os import environ as env

from fiwareskuld.expired_users import ExpiredUsers
from fiwareskuld.utils.osclients import OpenStackClients
from fiwareskuld import utils


logger = utils.log.init_logs('phase0')

__author__ = 'chema'




def is_user_protected(usertocheck):
    """
    Return true if the user must not be deleted, because their address has a
    domain in setting.DONT_DELETE_DOMAINS, and print a warning.
    :param usertocheck: user to check
    :return: true if the user must not be deleted
    """
    domain = usertocheck.name.partition('@')[2]
    if domain in settings.DONT_DELETE_DOMAINS:
        logger.warning(
            'User with name %(name)s should not be deleted due to its domain',
            {'name': usertocheck.name})
        return True
    else:
        return False

logger.debug('Getting expired users')
(next_to_expire, expired_users) = ExpiredUsers(
    username=env['OS_USERNAME'], password=env['OS_PASSWORD'],
    tenant=env['OS_TENANT_NAME']).get_yellow_red_users()

osclients = OpenStackClients()

# Use an alternative URL that allow direct access to the keystone admin
# endpoint, because the registered one uses an internal IP address.

osclients.override_endpoint(
    'identity', osclients.region, 'admin', settings.KEYSTONE_ENDPOINT)

keystone = osclients.get_keystoneclientv3()


# build users map
logger.debug('Building user map')
users_by_id = dict()
for user in keystone.users.list():
    users_by_id[user.id] = user

with open('users_to_delete.txt', 'w') as fich_delete:
    logger.debug('Generating user delete list')
    for user_id in expired_users:
        if not is_user_protected(users_by_id[user_id]):
            fich_delete.write(user_id + "\n")

with open('users_to_notify.txt', 'w') as fich_notify:
    logger.debug('Generating user notification list')
    for user_id in next_to_expire:
        if not is_user_protected(users_by_id[user_id]):
            fich_notify.write(user_id + "\n")
