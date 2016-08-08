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


from unittest import TestCase
from datetime import datetime
import requests_mock
from fiwareskuld.expired_users import ExpiredUsers
from fiwareskuld.users_management import UserManager
from mock import patch
from test_openstackmap import MySessionMock
from os import environ as environ


@requests_mock.Mocker()
class TestExpiredUsers(TestCase):

    mock_session = MySessionMock()

    def setUp(self):
        self.OS_AUTH_URL = 'http://cloud.host.fi-ware.org:4731/v2.0'
        self.OS_USERNAME = 'user'
        self.OS_PASSWORD = 'password'
        self.OS_TENANT_NAME = 'user cloud'
        self.OS_TENANT_ID = "OS_TENANT_ID"
        self.OS_REGION_NAME = 'Spain2'
        self.OS_TRUST_ID = ''
        self.OS_KEYSTONE_ADMIN_ENDPOINT = 'http://cloud.lab.fiware.org:4730'

        environ.setdefault('OS_AUTH_URL', self.OS_AUTH_URL)
        environ.setdefault('OS_USERNAME', self.OS_USERNAME)
        environ.setdefault('OS_PASSWORD', self.OS_PASSWORD)
        environ.setdefault('OS_TENANT_NAME', self.OS_TENANT_NAME)
        environ.setdefault('OS_TENANT_ID', self.OS_TENANT_ID)
        environ.setdefault('OS_REGION_NAME', self.OS_REGION_NAME)
        environ.setdefault('OS_TRUST_ID', self.OS_TRUST_ID)

    @patch('fiwareskuld.utils.osclients.session', mock_session)
    def testlistTrialUsers(self, m):
        """testadmintoken check that we have an admin token"""
        expiredusers = ExpiredUsers('any tenant id', 'any username', 'any password')
        result = expiredusers.get_trial_users()

        expectedresult = ['user_trial1', 'user_trial2']

        self.assertEqual(expectedresult[0], result[0].id)
        self.assertEqual(expectedresult[1], result[1].id)

    @patch('fiwareskuld.utils.osclients.session', mock_session)
    def testlistCommunityUsers(self, m):
        """testadmintoken check that we have an admin token"""
        expiredusers = ExpiredUsers('any tenant id', 'any username', 'any password')
        result = expiredusers.get_community_users()

        expectedresult = ['user_community1', 'user_community2']

        self.assertEqual(expectedresult[0], result[0].id)
        self.assertEqual(expectedresult[1], result[1].id)

    @patch('fiwareskuld.utils.osclients.session', mock_session)
    def testTrialUsersExpired(self, m):
        """testadmintoken check that we have an admin token"""
        expiredusers = ExpiredUsers('any tenant id', 'any username', 'any password')
        result = expiredusers.get_list_expired_trial_users()

        expectedresult = ['user_trial1', 'user_trial2']

        self.assertEqual(len(expectedresult), len(result))
        for i in range(0, len(expectedresult) - 1):
            self.assertEqual(expectedresult[i], result[i].id)

    @patch('fiwareskuld.utils.osclients.session', mock_session)
    def testGetRoleUser(self, m):
        """testadmintoken check that we have an admin token"""
        expiredusers = ExpiredUsers('any tenant id', 'any username', 'any password')
        user_manager = UserManager()
        user = user_manager.get_user("user_trial1")
        result = expiredusers.get_roles_user(user)
        self.assertIn("trial", result)

    @patch('fiwareskuld.utils.osclients.session', mock_session)
    def testCommunityUsersExpired(self, m):
        """testadmintoken check that we have an admin token"""
        expiredusers = ExpiredUsers('any tenant id', 'any username', 'any password')
        result = expiredusers.get_list_expired_community_users()
        expectedresult = ['user_community1', 'user_community2']
        self.assertEqual(result[0].id, expectedresult[0])
        self.assertEqual(result[1].id, expectedresult[1])

    @patch('fiwareskuld.utils.osclients.session', mock_session)
    def testcheckTime1(self, m):
        """ test the difference between two dates in string are bigger than 14 days."""
        expiredusers = ExpiredUsers('any tenant id', 'any username', 'any password')

        olddate = "2015-05-01"

        result = expiredusers.check_time(olddate, 100)

        expectedresult = True

        self.assertEqual(expectedresult, result)

    @patch('fiwareskuld.utils.osclients.session', mock_session)
    def testcheckTime2(self, m):
        """ test the difference between two dates in string are bigger than 14 days."""
        expiredusers = ExpiredUsers('any tenant id', 'any username', 'any password')

        aux = datetime.today()
        olddate = aux.strftime("%Y-%m-%d")

        result = expiredusers.check_time(olddate, 100)

        expectedresult = False

        self.assertEqual(expectedresult, result)

    @patch('fiwareskuld.utils.osclients.session', mock_session)
    def testget_yellow_red_users(self, m):
        """ Test that we obtain the correct list of expired users and the
            lists of user to be expired in the next days.
        """
        expiredusers = ExpiredUsers('any tenant id', 'any username', 'any password')

        (yellow, red) = expiredusers.get_yellow_red_trial_users()

        expectedyellow = []
        expectedred = ['user_trial1', 'user_trial2']

        self.assertEqual(len(expectedyellow), len(yellow))
        for i in range(0, len(expectedyellow) - 1):
            self.assertEqual(expectedyellow[i], yellow[i].id)

        self.assertEqual(len(expectedred), len(red))
        for i in range(0, len(expectedred) - 1):
            self.assertEqual(expectedred[i], red[i].id)

    @patch('fiwareskuld.utils.osclients.session', mock_session)
    def test_listusers(self, m):
        """ Test that we obtain the correct list of expired users.
        """
        expiredusers = ExpiredUsers('any tenant id', 'any username', 'any password')

        result = expiredusers.get_users()
        self.assertEqual(len(result), 4)
