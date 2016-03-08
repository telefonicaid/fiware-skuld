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
from fiwareskuld.utils import log
from fiwareskuld.change_password import PasswordChanger

__author__ = 'chema'

logger = log.init_logs('phase1')

try:
    users_to_delete = open('users_to_delete.txt')

    users_credentials = open('users_credentials.txt', 'w')

    user_manager = PasswordChanger()
    user_ids = list()
    for user in users_to_delete.readlines():
        user_ids.append(user.strip())
    cred_list = user_manager.get_list_users_with_cred(user_ids)

    for cred in cred_list:
        users_credentials.write(','.join(cred) + '\n')

    users_credentials.close()
except Exception:
    logger.error('The users_to_delete.txt file must exists')
