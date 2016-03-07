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


import json
import requests
from datetime import datetime
from conf import settings
from utils.log import logger


class ExpiredUsers:
    def __init__(self, tenant=None, username=None, password=None):
        """ Initialize the class with the appropriate parameters.
        """
        self.TRIAL_ROLE_ID = settings.TRIAL_ROLE_ID
        self.BASIC_ROLE_ID = settings.BASIC_ROLE_ID
        self.KEYSTONE_ENDPOINT = settings.KEYSTONE_ENDPOINT
        self.v20 = "v2.0/"
        self.v30 = "v3/"
        self.token = None
        self.listUsers = []
        self.MAX_NUMBER_OF_DAYS = settings.MAX_NUMBER_OF_DAYS
        self.finalList = []
        self.yellowList = []
        self.__tenant = tenant
        self.__username = username
        self.__password = password

    def get_admin_token(self):
        """
        Return the admin token for a administrator user, this value is
        maintained in the internal attribute "token" of the class.
        :return: The admin token to be used in the X-Auth-Token header
        """

        self.__check_credentials()

        payload = "{\"auth\":{\"tenantName\":\"%s\"," \
                  "\"passwordCredentials\":" \
                  "{\"username\":\"%s\",\"password\":\"%s\"}}}" \
                  % (self.__tenant, self.__username, self.__password)
        headers = {'content-type': 'application/json'}
        url = self.KEYSTONE_ENDPOINT + self.v20 + "tokens"
        r = requests.post(url=url, data=payload, headers=headers)

        rjson = json.loads(r.text)

        if r.status_code == 200:

            self.token = rjson['access']['token']['id']

            logger.info("Admin token requested: %s", self.token)
        else:
            raise Exception(rjson['error']['message'])

        return self.token

    def get_list_trial_users(self):
        """
        Return the list of users which have the Trial Role defined. This value
        is maintained in the internal attribute "listUsers" of the class.
        :return: Lists of users id who have Trial role
        """
        self.__check_token()

        url = self.KEYSTONE_ENDPOINT + self.v30 + \
            "role_assignments?role.id=" + self.TRIAL_ROLE_ID
        headers = {'X-Auth-Token': self.token}
        r = requests.get(url=url, headers=headers)

        role_assignments = json.loads(r.text)['role_assignments']

        # Extract the list of user_ids
        for item in role_assignments:
            self.listUsers.append(item['user']['id'])

        logger.info("Number of Trial users detected: %d", len(self.listUsers))

        return self.listUsers

    def get_yellow_red_users(self):

        # Get the security token
        self.get_admin_token()

        # Get the list of Trial users
        self.get_list_trial_users()

        self.__check_token()

        url = self.KEYSTONE_ENDPOINT + self.v30 + "users/"
        headers = {'X-Auth-Token': self.token}

        # Extract the list of user_ids
        for user_id in self.listUsers:
            finalurl = url + user_id
            r = requests.get(url=finalurl, headers=headers)

            user = json.loads(r.text)['user']
            remaining = self.get_trial_remaining_time(user)

            if remaining < 0:
                # It means that the user trial period has expired
                self.finalList.append(user_id)
            elif remaining <= settings.NOTIFY_BEFORE_EXPIRED:
                # It means that the user trial period is going to expire in
                # a week or less.
                self.yellowList.append(user_id)

        logger.info("Number of expired Trial Users found: %d",
                    len(self.finalList))
        logger.info("Number of Trial Users to expire in the following days:"
                    "%d", len(self.yellowList))

        return self.yellowList, self.finalList

    def get_list_expired_users(self):
        """
        For each users id that have the Trial role, we need to check
        if the time from their creation (trial_created_at) have
        expired. This value is maintained in the internal attribute
        "finalList" of the class.
        :return: Lists of Users id who have Trial role and expired
        """

        self.__check_token()

        url = self.KEYSTONE_ENDPOINT + self.v30 + "users/"
        headers = {'X-Auth-Token': self.token}

        # Extract the list of user_ids
        for user_id in self.listUsers:
            finalurl = url + user_id
            r = requests.get(url=finalurl, headers=headers)

            user = json.loads(r.text)['user']
            trial_started_at = user['trial_started_at']
            trial_duration = user.get(
                'trial_duration', self.MAX_NUMBER_OF_DAYS)

            if self.check_time(trial_started_at, trial_duration):
                # If true means that the user trial period has expired
                self.finalList.append(user_id)

        logger.info("Number of expired users found: %d", len(self.finalList))

        return self.finalList

    def check_time(self, trial_started_at,
                   trial_duration=settings.MAX_NUMBER_OF_DAYS):
        """
        Check the time of the trial user in order to see if it is expired.
        :param trial_started_at: the date in which the trial user was created
        :return: True if the trial period was expired (greater than
                 settings.MAX_NUMBER_OF_DAYS).
                 False anyway
        """

        formatter_string = "%Y-%m-%d"

        datetime_object = datetime.strptime(trial_started_at, formatter_string)
        date_object_old = datetime_object.date()

        datetime_object = datetime.today()
        date_object_new = datetime_object.date()

        difference = date_object_new - date_object_old

        if difference.days > trial_duration:
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

        trial_started_at = user['trial_started_at']
        trial_duration = user.get(
            'trial_duration', self.MAX_NUMBER_OF_DAYS)

        formatter_string = "%Y-%m-%d"

        datetime_object = datetime.strptime(trial_started_at, formatter_string)
        date_object_old = datetime_object.date()

        datetime_object = datetime.today()
        date_object_new = datetime_object.date()

        difference = date_object_new - date_object_old

        return trial_duration - difference.days

    def __check_token(self):
        """Check if the token is not blank"""
        if self.token == "":
            # We need to have a admin token in order to proceed.
            raise ValueError("Error, you need to have an admin token."
                             "Execute the get_admin_token method previously.")

    def __check_credentials(self):
        """Check if we have the credentials of the admin user"""
        if self.__tenant is None or self.__username is None\
                or self.__password is None:
            # We need to have a admin token in order to proceed.
            raise ValueError("Error, you need to define the credentials of the"
                             "admin user. Please, execute the setCredentials()"
                             "method previously.")

    def getadmintoken(self):
        """
        Get the current admin token
        :return: The Keystone admin token
        """
        return self.token

    def gerlisttrialusers(self):
        """
        Get the list of trial users
        :return: List of Trial users.
        """
        return self.listUsers

    def getlistusers(self):
        """
        Global method that call the rest of internal one in order to recover
        the information of the expired users.
        :return: List of Expired Users id who have Trial role and expired,
            example: ['0f4de1ea94d342e696f3f61320c15253',
                        '24396976a1b84eafa5347c3f9818a66a']
        """
        # Get the security token
        self.get_admin_token()

        # Get the list of Trial users
        self.get_list_trial_users()

        # Get the list of expired trial users
        listusers = self.get_list_expired_users()

        return listusers

    def set_keystone_endpoint(self, serviceendpoint):
        """ Set the service endpoint corresponding to the Keystone Service
        :param serviceendpoint: The Keystone service endpoint
        :return: None
        """
        self.KEYSTONE_ENDPOINT = serviceendpoint

    def get_keystone_endpoint(self):
        """ Get the Keystone service endpoint.
        :return: The Keystone service endpoint
        """
        return self.KEYSTONE_ENDPOINT
