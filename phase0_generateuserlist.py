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
author = 'chema'

import logging
from os import environ as env

from expired_users import ExpiredUsers
from settings import settings
from osclients import OpenStackClients

logging.debug('Getting expired users')
expired_users = ExpiredUsers(
    username=env['OS_USERNAME'], password=env['OS_PASSWORD'],
    tenant=env['OS_TENANT_NAME']).getlistusers()

dont_delete_domains = settings.DONT_DELETE_DOMAINS
osclients = OpenStackClients()

# Use an alternative URL that allow direct access to the keystone admin
# endpoint, because the registered one uses an internal IP address.

osclients.override_endpoint(
    'identity', osclients.region, 'admin', settings.KEYSTONE_ENDPOINT)

keystone = osclients.get_keystoneclientv3()

fich = open('users_to_delete.txt', 'w')

# build users map
logging.debug('Building user map')
users_by_id = dict()
for user in keystone.users.list():
    users_by_id[user.id] = user

logging.debug('Generating user list')
for user_id in expired_users:
    user = users_by_id[user_id]
    # print unicode(user).encode('utf8')
    domain = user.name.partition('@')[2]
    if domain != '' and domain in dont_delete_domains:
        logging.warning(
            'User with name %(name)s should not be deleted because the domain',
            {'name': user.name})
    else:
        print >>fich, user_id

fich.close()
