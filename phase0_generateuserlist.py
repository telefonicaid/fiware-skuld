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

expired_users = ExpiredUsers(
    username=env['OS_USERNAME'], password=['OS_PASSWORD'],
    tenant=['OS_TENANT_NAME']).getlistusers()

dont_delete_domains = settings.DONT_DELETE_DOMAINS
keystone = OpenStackClients().get_keystoneclientv3()

fich = open('users_to_delete.txt', 'w')

# build users map
users_by_id = dict()
for user in keystone.users.list():
    users_by_id[user.id] = user

for user_id in expired_users:
    user = users_by_id[user_id]
    print user
    domain = user.name.partition('@')[2]
    if domain != '' and domain in dont_delete_domains:
        msg = 'User with name {1} should not be deleted because the domain'
        logging.warning(msg.format(user.name))
    else:
        print >>fich, user_id

fich.close()

