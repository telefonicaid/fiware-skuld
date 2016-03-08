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

import queries
from utils.osclients import osclients
from conf import settings

q = queries.Queries()


class CheckUsers(object):
    """This class is for checking that the users that were converted to basic
    are still basic users before deleting their resources"""

    def __init__(self):
        """constructor, build the list of basic users included in
        users_to_delete.txt"""
        basic_type = settings.BASIC_ROLE_ID
        self.ids = set(
            line.strip() for line in open('users_to_delete.txt').readlines())
        keystone = osclients.get_keystoneclientv3()
        self.users_basic = set(
            asig.user['id']
            for asig in keystone.role_assignments.list(domain='default')
            if asig.role['id'] == basic_type and asig.user['id'] in self.ids)

    def report_not_basic_users(self):
        """report if there are users to delete that are not basic now"""
        no_basic_users = self.ids - self.users_basic
        if not no_basic_users:
            print('All is OK')
        else:
            print 'Users that are not basic: ', no_basic_users
            for user in no_basic_users:
                try:
                    user_type = q.get_type_fiware_user(user)
                except Exception:
                    user_type = 'unkown'
                print(user + ' ' + user_type)

if __name__ == '__main__':
    check = CheckUsers()
    check.report_not_basic_users()
