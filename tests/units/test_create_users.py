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
import requests_mock
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

        """It tests the creation of a none existing user"""
        createusers = UserManager()
        result = createusers.get_user("anynoexistinguser")
        self.assertIsNone(result)

    @patch('fiwareskuld.utils.osclients.session', mock_session)
    def testDeleteUser(self, m):

        """It tests the deletiong of a user"""
        createusers = UserManager()
        user = createusers.get_user("user_trial1")
        result = createusers.delete_user(user)
        self.assertIsNone(result)

    @patch('fiwareskuld.utils.osclients.session', mock_session)
    def testDeleteUserId(self, m):

        """It tests the deletion of a user by its id"""
        createusers = UserManager()
        result = createusers.delete_user_id("user_trial1")
        self.assertIsNone(result)

    @patch('fiwareskuld.utils.osclients.session', mock_session)
    def testGenerateTrustId(self, m):
        """It tests the generation of a trustid"""
        createusers = UserManager()
        name, trustid, id = createusers.generate_trust_id("user_trial1")
        self.assertEquals(trustid, "trustid")

    @patch('fiwareskuld.utils.osclients.session', mock_session)
    def testChangeToBasicUser(self, m):

        """It tests changing to basic user"""
        createusers = UserManager()
        user = createusers.get_user("user_trial1")
        result = createusers.change_to_basic_user_keystone(user)
        self.assertIsNone(result)
