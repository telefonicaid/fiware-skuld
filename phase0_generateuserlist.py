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

from expired_users import ExpiredUsers
from os import environ as env

expired_users = ExpiredUsers(
    username=env['OS_USERNAME'], password=['OS_PASSWORD'],
    tenant=['OS_TENANT_NAME'])

expired_users.get_list_trial_users()
users = expired_users.get_list_expired_users()
fich = users_to_delete = open('users_to_delete.txt', 'w')
for user in users:
    print >>fich, user
fich.close()

