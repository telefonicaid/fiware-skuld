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
from datetime import datetime

from fiwareskuld.conf import settings
import os.path
from os import environ as env
from fiwareskuld.utils import osclients
from fiwareskuld import utils
from fiwareskuld.utils import log
from fiwareskuld.utils import rotated_files


__author__ = 'chema'

logger = utils.log.init_logs('phase0')

env['OS_USERNAME'] = "idm"
env['OS_PASSWORD'] = "idm"
env['OS_TENANT_NAME'] = "idm"
env["OS_AUTH_URL"]= "http://130.206.120.23:5000/v3"
env["OS_REGION_NAME"]="Valladolid"
env["OS_PROJECT_DOMAIN_NAME"]="default"
env["OS_IDENTITY_API_VERSION"]="3"


class ExpiredUsers:
    def __init__(self):
        """Constructor. Create a keystone client"""
        clients = osclients.OpenStackClients()
        clients.override_endpoint(
            'identity', clients.region, 'admin', settings.KEYSTONE_ENDPOINT)
        self.keystoneclient = clients.get_keystoneclientv3()
        self.protected = set()

    def get_trial_user_ids(self):
        """Get a set of trial users; only the ids
        :return: a set of user ids, corresponding to trial users.
        """
        k = self.keystoneclient
        role = k.roles.find(name="trial")
        return set(e.user['id'] for e in k.role_assignments.list(
            role=role.id))

    def get_community_user_ids(self):
        """Get a set of community users; only the ids
        :return: a set of user ids, corresponding to trial users.
        """
        k = self.keystoneclient
        role = k.roles.find(name="community")
        return set(e.user['id'] for e in k.role_assignments.list(
            role=role.id))

    def get_basic_users_ids(self):
        """Get a set of basic users; only the ids
        :return: a set of user ids, corresponding to trial users.
        """
        k = self.keystoneclient
        role = k.roles.find(name="basic")
        return set(e.user['id'] for e in k.role_assignments.list(
            role=role.id))

    def get_trial_users(self):
        """Get the list of trial users; the full objects are included.
        :return: a list of trial users
        """
        user_ids = self.get_trial_user_ids()
        return list(user for user in self.keystoneclient.users.list() if user.id in user_ids)

    def get_community_users(self):
        """Get the list of trial users; the full objects are included.
        :return: a list of trial users
        """
        user_ids = self.get_community_user_ids()
        return list(user for user in self.keystoneclient.users.list() if user.id in user_ids)

    def get_yellow_red_trial_users(self):
        """Get a pair of lists
        * trail user accounts that are next to expire (i.e. less than
        NOTIFY_BEFORE_EXPIRE days): yellow users
        * trail user accounts that are already expired: red users
        :return: a tuple with two lists: users next to expire and expired"""
        red_users = list()
        yellow_users = list()

        for user in self.get_trial_users():
            remaining = self._get_remaining_trial_time(user.to_dict())
            if self._is_user_protected(user):
                self.protected.add(user)
                continue
            if remaining < 0:
                red_users.append(user)
            elif remaining <= settings.NOTIFY_BEFORE_EXPIRED:
                yellow_users.append(user)

        return yellow_users, red_users

    def get_yellow_red_community_users(self):
        """Get a pair of lists
        * trail user accounts that are next to expire (i.e. less than
        NOTIFY_BEFORE_EXPIRE days): yellow users
        * trail user accounts that are already expired: red users
        :return: a tuple with two lists: users next to expire and expired"""
        red_users = list()
        yellow_users = list()

        for user in self.get_community_users():
            remaining = self._get_remaining_community_time(user.to_dict())
            if self._is_user_protected(user):
                self.protected.add(user)
                continue
            if remaining < 0:
                red_users.append(user)
            elif remaining <= settings.NOTIFY_BEFORE_EXPIRED:
                yellow_users.append(user)

        return yellow_users, red_users

    def save_lists(self, cron_daily=False):
        """Create files users_to_delete.txt and users_to_notify.txt with the
        users expired and users that will expire in a week or less.

        If settings.STOP_BEFORE_DELETE !=0 and cron_daily=True, it also creates
        users_to_delete_phase3.txt (in this case, users_to_delete.txt is for
        the phase2). To create the file users_to_delete_phase3.txt, the files
        users_to_delete.txt are rotated in each daily execution; when the file
        reaches the settings.STOP_BEFORE_DELETE rotation, the file is renamed
        to users_to_delete_phase3.txt.

        if settings.STOP_BEFORE_DELETE ==0 and cron_daily=True, file
        users_to_delete.txt is renamed to users_to_delete_phase3.txt.

        :param cron_daily: this code is invoked from a cron daily script.
          if implies the creation of file users_to_delete_phase3.txt
        :return: nothing
        """
        (notify_list, delete_list) = self.get_yellow_red_trial_users()
        with open('users_to_notify.txt', 'w') as users_to_notify:
            for user in notify_list:
                users_to_notify.write(user.id + "\n")

        if cron_daily:
            if settings.STOP_BEFORE_DELETE == 1:
                name = 'users_to_delete_phase3.txt'
                with open(name, 'w') as users_to_delete_p3:
                    for user in delete_list:
                        users_to_delete_p3.write(user.id + ',' + user.name + '\n')
            else:
                name = 'users_to_delete.txt'
                phase3_name = 'users_to_delete_phase3.txt'
                basic_users = self.get_basic_users_ids()
                rotated_files.rotate_files(
                    name, settings.STOP_BEFORE_DELETE, phase3_name)
                # Remove from list the users that are not basic
                # (i.e.) users who has changed to community or again to trial
                if os.path.exists(phase3_name):
                    with open(phase3_name, 'r') as phase3:
                        filtered = list(u for u in phase3 if u in basic_users)
                    with open(phase3_name, 'w') as phase3:
                        for user in filtered:
                            phase3.write(user.id + ',' + user.name + '\n')

                with open(name, 'w') as users_to_delete:
                    for user in delete_list:
                        users_to_delete.write(user.id + '\n')

        else:
            with open('users_to_delete.txt', 'w') as users_to_delete:
                for user in delete_list:
                    users_to_delete.write(user.id + ',' + user.name + '\n')

    def save_lists_community(self, cron_daily=False):
        """Create files users_to_delete.txt and users_to_notify.txt with the
        users expired and users that will expire in a week or less.

        If settings.STOP_BEFORE_DELETE !=0 and cron_daily=True, it also creates
        users_to_delete_phase3.txt (in this case, users_to_delete.txt is for
        the phase2). To create the file users_to_delete_phase3.txt, the files
        users_to_delete.txt are rotated in each daily execution; when the file
        reaches the settings.STOP_BEFORE_DELETE rotation, the file is renamed
        to users_to_delete_phase3.txt.

        if settings.STOP_BEFORE_DELETE ==0 and cron_daily=True, file
        users_to_delete.txt is renamed to users_to_delete_phase3.txt.

        :param cron_daily: this code is invoked from a cron daily script.
          if implies the creation of file users_to_delete_phase3.txt
        :return: nothing
        """
        (notify_list, delete_list) = self.get_yellow_red_community_users()
        with open('users_to_notify_community.txt', 'w') as users_to_notify:
            for user in notify_list:
                users_to_notify.write(user.id + "\n")

        if cron_daily:
            if settings.STOP_BEFORE_DELETE == 0:
                name = 'users_to_delete_community_phase3.txt'
                with open(name, 'w') as users_to_delete_p3:
                    for user in delete_list:
                        users_to_delete_p3.write(user.id + ',' + user.name + '\n')
            else:
                name = 'users_to_delete_community.txt'
                phase3_name = 'users_to_delete_phase3_community.txt'
                basic_users = self.get_basic_users_ids()
                utils.rotated_files.rotate_files(
                    name, settings.STOP_BEFORE_DELETE, phase3_name)
                # Remove from list the users that are not basic
                # (i.e.) users who has changed to community or again to trial
                if os.path.exists(phase3_name):
                    with open(phase3_name, 'r') as phase3:
                        filtered = list(u for u in phase3 if u in basic_users)
                    with open(phase3_name, 'w') as phase3:
                        for user in filtered:
                            phase3.write(user.id + ',' + user.name + '\n')

                with open(name, 'w') as users_to_delete:
                    for user in delete_list:
                        users_to_delete.write(user.id + '\n')

        else:
            with open('users_to_delete_community.txt', 'w') as users_to_delete:
                for user in delete_list:
                    users_to_delete.write(user.id + ',' + user.name + '\n')

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

    def _get_remaining_community_time(self, user):
        """
        Check the time of the trial user; return the remaining days.
        The number will be negative when the account is expired.
        :param user: the trial user data obtained from keystone API server
        :return: remaining days (may be negative)
        """

        community_started_at = user['community_started_at']
        community_duration = user.get(
            'community_duration', settings.MAX_NUMBER_OF_DAYS)

        formatter_string = "%Y-%m-%d"

        datetime_object = datetime.strptime(community_started_at, formatter_string)
        date_object_old = datetime_object.date()

        datetime_object = datetime.today()
        date_object_new = datetime_object.date()

        difference = date_object_new - date_object_old

        return community_duration - difference.days

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
    expired.save_lists(cron_daily=True)
    expired.save_lists_community(cron_daily=True)
