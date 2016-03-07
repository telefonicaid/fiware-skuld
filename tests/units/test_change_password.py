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


from os import environ
from unittest import TestCase
from fiwareskuld import change_password
from mock import patch
from test_openstackmap import MySessionMock, OS_TENANT_ID


class TestChangePassword(TestCase):
    mock_session2 = MySessionMock()

    def setUp(self):
        self.mock_user_name = 'user'

        self.OS_AUTH_URL = 'http://cloud.lab.fi-ware.org:4731/v2.0'
        self.OS_USERNAME = 'user'
        self.OS_PASSWORD = 'password'
        self.OS_TENANT_NAME = 'user cloud'
        self.OS_TENANT_ID = OS_TENANT_ID
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

    @patch('fiwareskuld.utils.osclients.session', mock_session2)
    def test_get_user_by_name(self):
        """test_get_user_by_name check that we could get a user by name."""
        password_changer = change_password.PasswordChanger()
        user = password_changer.get_user_byname(self.mock_user_name)
        self.assertEqual(self.mock_user_name, user.name)

    @patch('fiwareskuld.utils.osclients.session', mock_session2)
    def test_get_user_by_id(self):
        """test_get_user_by_id check that we could get a user by id."""
        password_changer = change_password.PasswordChanger()
        user = password_changer.get_user_byid(OS_TENANT_ID)
        self.assertEqual(OS_TENANT_ID, user.id)

    @patch('fiwareskuld.utils.osclients.session', mock_session2)
    def test_get_list_users_with_cred(self):
        """test_get_list_users_with_cred check that we could patch the
        Password to a list of users"""
        password_changer = change_password.PasswordChanger()
        mylist = []
        mylist.append(OS_TENANT_ID)
        result = password_changer.get_list_users_with_cred(mylist)
        self.assertIsNotNone(result)
