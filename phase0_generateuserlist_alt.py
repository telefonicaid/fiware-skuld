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

import osclients

from settings import settings
from datetime import datetime
import utils.log

logger = utils.log.init_logs('phase0')

class ExpiredUsers():
    def __init__(self):
        """Constructor. Create a keystone client"""
        clients = osclients.OpenStackClients()
        clients.override_endpoint(
            'identity', clients.region, 'admin', settings.KEYSTONE_ENDPOINT)
        self.keystoneclient = clients.get_keystoneclientv3()

    def get_trial_user_ids(self):
        """Get the list of trial users; only the ids
        :return: a list of user ids, corresponding to trial users.
        """
        k = self.keystoneclient
        return set(e.user['id'] for e in k.role_assignments.list(
            role=settings.TRIAL_ROLE_ID))

    def get_trial_users(self):
        """Get the list of trial users; the full objects are included.
        :return: a list of trial users
        """
        user_ids = self.get_trial_user_ids()
        return list(user for user in self.keystoneclient.users.list()
                     if user.id in user_ids)

    def get_yellow_red_users(self):
        """Get a pair of lists
        * trail user accounts that are next to expire (7 days): yellow users
        * trail user accounts that are already expired: red users
        :return: a tuple with two lists: users next to expire and expired"""
        red_users = list()
        yellow_users = list()

        for user in self.get_trial_users():
            remaining = self._get_remaining_trial_time(user.to_dict())
            if self._is_user_protected(user):
                continue
            if remaining < 0:
                red_users.append(user)
            elif remaining <= settings.NOTIFY_BEFORE_EXPIRED:
                yellow_users.append(user)

        return yellow_users, red_users

    def get_yellow_orange_red_users(self):
        """Get three lists:
          * trail user accounts that are next to expire (i.e. less than
          NOTIFY_BEFORE_EXPIRED days): yellow users
          * trail user accounts that are already expired, but less than
           STOP_BEFORE_DELETE days: orange users
          * trail user accounts that are expired for more than
            STOP_BEFORE_DELETE: red users

        :return: a tuple with three list
        """
        red_users = list()
        yellow_users = list()
        orange_users = list()

        for user in self.get_trial_users():
            remaining = self._get_remaining_trial_time(user.to_dict())
            if self._is_user_protected(user):
                continue
            if remaining < - settings.STOP_BEFORE_DELETE:
                red_users.append(user)
            elif remaining < 0:
                orange_users.append(user)
            elif remaining <= settings.NOTIFY_BEFORE_EXPIRED:
                yellow_users.append(user)

        return yellow_users, orange_users, red_users

    def save_lists(self):
        """Create files users_to_delete.txt and users_to_notify.txt with the
        users expired and users that will expire in a week or less.
        :return: nothing
        """
        (notify_list, delete_list) = self.get_yellow_red_users()
        with open('users_to_delete.txt', 'w') as users_to_delete:
            for user in delete_list:
                print >>users_to_delete, user.id
        with open('users_to_notify.txt', 'w') as users_to_notify:
            for user in notify_list:
                print >>users_to_notify, user.id

    def _get_remaining_trial_time(self, user):
        """
        Check the time of the trial user; return the remaining days.
        The number will be negative when the account is expired.
        :param user: the trial user data obtained from keystone API server
        :return: remaining days (may be negative)
        """

        trial_started_at = user['trial_started_at']
        trial_duration = user.get(
            'trial_duration', settings.MAX_NUMBER_OF_DAYS)

        formatter_string = "%Y-%m-%d"

        datetime_object = datetime.strptime(trial_started_at, formatter_string)
        date_object_old = datetime_object.date()

        datetime_object = datetime.today()
        date_object_new = datetime_object.date()

        difference = date_object_new - date_object_old

        return trial_duration - difference.days

    def _is_user_protected(self, user):
        """
        Return true if the user must not be deleted, because their address has a
        domain in setting.DONT_DELETE_DOMAINS, and print a warning.
        :param user: user to check
        :return: true if the user must not be deleted
        """
        domain = user.name.partition('@')[2]
        if domain != '' and domain in settings.DONT_DELETE_DOMAINS:
            logger.warning(
                'User with name %(name)s should not be deleted because the '
                'domain',
                {'name': user.name})
            return True
        else:
            return False


if __name__ == '__main__':
    expired = ExpiredUsers()
    expired.save_lists()
