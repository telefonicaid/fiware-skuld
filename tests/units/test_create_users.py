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
class TestCreateUsers(TestCase):

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
    def testCreateTrialUser(self, m):

        """It tests the creation of a trial user"""
        createusers = UserManager()
        result = createusers.register_user("user_trial1", "anypassword", "trial")
        self.assertIsNotNone(result)

    @patch('fiwareskuld.utils.osclients.session', mock_session)
    def testCreateCommunityUser(self, m):

        """It tests the creation of a community user"""
        createusers = UserManager()
        result = createusers.register_user("user_community1", "anypassword", "community")
        self.assertIsNotNone(result)

    @patch('fiwareskuld.utils.osclients.session', mock_session)
    def testExistingUser(self, m):

        """It tests the creation of a community user"""
        createusers = UserManager()
        result = createusers.get_user("user_trial1")
        self.assertIsNotNone(result)

    @patch('fiwareskuld.utils.osclients.session', mock_session)
    def testNotExistingUser(self, m):

        """It tests the creation of a community user"""
        createusers = UserManager()
        result = createusers.get_user("anynoexistinguser")
        self.assertIsNone(result)

    @patch('fiwareskuld.utils.osclients.session', mock_session)
    def testDeleteCommunityUsers(self, m):

        """It tests the deletion of the community users"""
        createusers = UserManager()
        createusers._delete_community_users()

    @patch('fiwareskuld.utils.osclients.session', mock_session)
    def testDeleteTrialUsers(self, m):

        """It tests the deletion of the trial users"""
        createusers = UserManager()
        createusers._delete_trial_users()
