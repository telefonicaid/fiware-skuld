# -*- coding: utf-8 -*-

# Copyright 2015 Telefónica Investigación y Desarrollo, S.A.U
#
# This file is part of FIWARE project.
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


import datetime
import os

from fiwareskuld.conf import settings
from fiwareskuld.utils.log import logger
from fiwareskuld.utils import osclients
from fiwareskuld.utils import rotated_files


class ExpiredUsers:
    def __init__(self, tenant=None, username=None, password=None):
        """Constructor. Create a keystone client"""
        self.__tenant = tenant
        self.__username = username
        self.__password = password
        clients = osclients.OpenStackClients()
        clients.override_endpoint(
            'identity', clients.region, 'admin', settings.KEYSTONE_ENDPOINT)
        self.TRIAL_MAX_NUMBER_OF_DAYS = settings.TRIAL_MAX_NUMBER_OF_DAYS
        self.COMMUNITY_MAX_NUMBER_OF_DAYS = settings.COMMUNITY_MAX_NUMBER_OF_DAYS
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

    def get_roles_user(self, user):
        return self.get_roles_user_id(user.id)

    def get_roles_user_id(self, user_id):

        user_r = self.keystoneclient.role_assignments.list(user=user_id)
        roles = []
        for us in user_r:
            roles.append(self.get_role_name_by_id(us.role["id"]))
        return roles

    def get_role_name_by_id(self, role_id):
        roles = self.keystoneclient.roles.list()
        for role in roles:
            if role_id == role.id:
                return role.name

    def get_community_user_ids(self):
        """Get a set of community users; only the ids
        :return: a set of user ids, corresponding to community users.
        """
        k = self.keystoneclient
        role = k.roles.find(name="community")
        return set(e.user['id'] for e in k.role_assignments.list(
            role=role.id))

    def get_basic_users_ids(self):
        """Get a set of basic users; only the ids
        :return: a set of user ids, corresponding to basic users.
        """
        k = self.keystoneclient
        role = k.roles.find(name="basic")
        return set(e.user['id'] for e in k.role_assignments.list(
            role=role.id))

    def get_basic_users(self):
        """Get the list of basic users; the full objects are included.
        :return: a list of basic users
        """
        user_ids = self.get_basic_users_ids()
        return list(user for user in self.keystoneclient.users.list() if user.id in user_ids)

    def get_trial_users(self):
        """Get the list of trial users; the full objects are included.
        :return: a list of trial users
        """
        user_ids = self.get_trial_user_ids()
        return list(user for user in self.keystoneclient.users.list() if user.id in user_ids)

    def get_community_users(self):
        """Get the list of community users; the full objects are included.
        :return: a list of community users
        """
        user_ids = self.get_community_user_ids()

        d = list(user for user in self.keystoneclient.users.list() if user.id in user_ids)
        return d

    def get_users(self):
        """Get the list of users; the full objects are included.
        :return: a list of users
        """
        return self.keystoneclient.users.list()

    def get_yellow_red_trial_users(self):

        # Get the security token

        # Get the list of Trial users
        users = self.get_trial_users()
        return self._get_red_yellow(users)

    def _get_red_yellow(self, users):
        finalList = []
        yellowList = []
        # Extract the list of user_ids
        for user in users:
            notify = 0
            role = self.get_role_trial_or_community(user)
            if not role:
                continue
            if role == "trial":
                notify = settings.NOTIFY_BEFORE_TRIAL_EXPIRED
            elif role == "community":
                notify = settings.NOTIFY_BEFORE_COMMUNITY_EXPIRED

            remaining = self.get_remaining_time(user)

            if remaining < 0:
                # It means that the user trial period has expired
                finalList.append(user)
            elif remaining <= notify:
                # It means that the user trial period is going to expire in
                # a week or less.
                yellowList.append(user)

        logger.info("Number of expired Trial Users found: %d",
                    len(finalList))
        logger.info("Number of Trial Users to expire in the following days: %d",
                    len(yellowList))

        return yellowList, finalList

    def get_yellow_red_community_users(self):

        # Get the security token

        # Get the list of Trial users
        users = self.get_community_users()
        return self._get_red_yellow(users)

    def get_list_expired_trial_users(self):
        """
        For each users id that have the Trial role, we need to check
        if the time from their creation (trial_created_at) have
        expired. This value is maintained in the internal attribute
        "finalList" of the class.
        :return: Lists of Users id who have Trial role and expired
        """
        users = self.get_trial_users()
        finalList = []

        # Extract the list of user_ids
        for user in users:
            if not user.trial_started_at:
                continue
            trial_started_at = user.trial_started_at
            if hasattr(user, 'trial_duration'):
                trial_duration = user.trial_duration
            else:
                trial_duration = self.TRIAL_MAX_NUMBER_OF_DAYS
            if self.check_time(trial_started_at, trial_duration):
                # If true means that the user trial period has expired
                finalList.append(user)

        logger.info("Number of expired users found: %d", len(finalList))

        return finalList

    def get_list_expired_community_users(self):
        """
        For each users id that have the Trial role, we need to check
        if the time from their creation (trial_created_at) have
        expired. This value is maintained in the internal attribute
        "finalList" of the class.
        :return: Lists of Users id who have Trial role and expired
        """
        users = self.get_community_users()
        finalList = []

        # Extract the list of user_ids
        for user in users:
            community_started_at = user.community_started_at
            if hasattr(user, 'community_duration'):
                community_duration = user.community_duration
            else:
                community_duration = self.COMMUNITY_MAX_NUMBER_OF_DAYS

            if self.check_time(community_started_at, community_duration):
                # If true means that the user trial period has expired
                finalList.append(user)

        logger.info("Number of expired users found: %d", len(finalList))

        return finalList

    def check_time(self, started_at, duration):
        """
        Check the time of the trial user in order to see if it is expired.
        :param trial_started_at: the date in which the trial user was created
        :return: True if the trial period was expired (greater than
                 settings.MAX_NUMBER_OF_DAYS).
                 False anyway
        """

        formatter_string = "%Y-%m-%d"
        datetime_object = datetime.datetime.strptime(started_at, formatter_string)
        date_object_old = datetime_object.date()

        datetime_object = datetime.datetime.today()
        date_object_new = datetime_object.date()

        difference = date_object_new - date_object_old

        if difference.days > duration:
            result = True
        else:
            result = False

        return result

    def get_role_trial_or_community(self, user):
        """
        It checks if the user has a role trial or
        community and in this case, it returns it.
        :param user: the user to check it
        :return: the role name
        """
        role = None
        roles = self.get_roles_user(user)
        if "trial" in roles:
            role = "trial"
        elif "community" in roles:
            role = "community"
        return role

    def get_remaining_time(self, user):
        """
        Check the time of the trial user; return the remaining days.
        The number will be negative when the account is expired.
        :param user: the trial user data obtained from keystone API server
        :return: remaining days (may be negative)
        """

        started_at = 0
        duration = 180
        role = self.get_role_trial_or_community(user)
        if not role:
            return duration

        if role == "trial":
            started_at = user.trial_started_at
            if hasattr(user, 'trial_duration'):
                duration = user.trial_duration
            else:
                duration = self.TRIAL_MAX_NUMBER_OF_DAYS
        elif role == "community":
            started_at = user.community_started_at
            if hasattr(user, 'community_duration'):
                duration = user.community_duration
            else:
                duration = self.COMMUNITY_MAX_NUMBER_OF_DAYS

        formatter_string = "%Y-%m-%d"

        datetime_object = datetime.datetime.strptime(started_at, formatter_string)
        date_object_old = datetime_object.date()

        datetime_object = datetime.datetime.today()
        date_object_new = datetime_object.date()

        difference = date_object_new - date_object_old

        return duration - difference.days

    def save_trial_lists(self, cron_daily=False):
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
        self.save_list(notify_list, delete_list, cron_daily)

    def save_community_lists(self, cron_daily=False):
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
        self.save_list(notify_list, delete_list, cron_daily)

    def save_list(self, notify_list, delete_list, cron_daily):
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
        with open('users_to_notify.txt', 'w') as users_to_notify:
            for user in notify_list:
                users_to_notify.write(user.id + "\n")

        if cron_daily:
            if settings.STOP_BEFORE_DELETE == 0:
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
