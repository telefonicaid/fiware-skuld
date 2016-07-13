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

from fiwareskuld.conf import settings
from fiwareskuld.utils.log import logger
from fiwareskuld.utils import osclients


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

    def get_role_user(self, user):
        k = self.keystoneclient
        user_r = k.role_assignments.list()
        for us in user_r:
            if us.user["id"] == user.id:
                return k.roles.list(id=us.role["id"])[0].name

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

    def get_yellow_red_users(self):

        # Get the security token

        # Get the list of Trial users
        users = self.get_trial_users()
        finalList = []
        yellowList = []

        # Extract the list of user_ids
        for user in users:
            remaining = self.get_trial_remaining_time(user)

            if remaining < 0:
                # It means that the user trial period has expired
                finalList.append(user.id)
            elif remaining <= settings.NOTIFY_BEFORE_EXPIRED:
                # It means that the user trial period is going to expire in
                # a week or less.
                yellowList.append(user.id)

        logger.info("Number of expired Trial Users found: %d",
                    len(finalList))
        logger.info("Number of Trial Users to expire in the following days: %d",
                    len(yellowList))

        return yellowList, finalList

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
                finalList.append(user.id)

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

    def get_trial_remaining_time(self, user):
        """
        Check the time of the trial user; return the remaining days.
        The number will be negative when the account is expired.
        :param user: the trial user data obtained from keystone API server
        :return: remaining days (may be negative)
        """

        trial_started_at = user.trial_started_at
        if hasattr(user, 'trial_duration'):
            trial_duration = user.trial_duration
        else:
            trial_duration = self.TRIAL_MAX_NUMBER_OF_DAYS

        formatter_string = "%Y-%m-%d"

        datetime_object = datetime.datetime.strptime(trial_started_at, formatter_string)
        date_object_old = datetime_object.date()

        datetime_object = datetime.datetime.today()
        date_object_new = datetime_object.date()

        difference = date_object_new - date_object_old

        return trial_duration - difference.days
