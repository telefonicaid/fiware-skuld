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


from os import environ, getcwd
from unittest import TestCase
from fiwareskuld import change_password
from mock import patch
from test_openstackmap import MySessionMock, MySessionFakeMock, MySessionFakeMock2, \
    OS_TENANT_ID, OS_TENANT_ID2
from test_check_users import ContextualStringIO
from tests_constants import NO_DATA


class TestChangePassword(TestCase):
    mock_session2 = MySessionMock()
    mock_session3 = MySessionFakeMock()
    mock_session4 = MySessionFakeMock2()

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

        dir = getcwd()
        if '/tests/units' in dir:
            self.list_users_response = open('./resources/list_users_response.json').read()
            self.get_users_response = open('./resources/get_user_response.json').read()
            self.list_users_response2 = open('./resources/list_users_response4.json').read()
        else:
            self.list_users_response = open('./tests/units/resources/list_users_response.json').read()
            self.get_users_response = open('./tests/units/resources/get_user_response.json').read()
            self.list_users_response2 = open('./tests/units/resources/list_users_response4.json').read()

    @patch('fiwareskuld.utils.osclients.session', mock_session2)
    def test_get_user_by_name(self):
        """test_get_user_by_name check that we could get a user by name."""
        passwordChanger = change_password.PasswordChanger()
        user = passwordChanger.get_user_byname(self.mock_user_name)
        self.assertEqual(self.mock_user_name, user.name)

    @patch('fiwareskuld.utils.osclients.session', mock_session2)
    def test_get_user_by_id(self):
        """test_get_user_by_id check that we could get a user by id."""
        passwordChanger = change_password.PasswordChanger()
        user = passwordChanger.get_user_byid(OS_TENANT_ID)
        self.assertEqual(OS_TENANT_ID, user.id)

    @patch('fiwareskuld.utils.osclients.session', mock_session2)
    def test_get_list_users_with_cred(self):
        """test_get_list_users_with_cred check that we could patch the Password to a list of users"""
        passwordChanger = change_password.PasswordChanger()
        mylist = []
        mylist.append(OS_TENANT_ID)
        result = passwordChanger.get_list_users_with_cred(mylist)
        self.assertIsNotNone(result)

    @patch('fiwareskuld.utils.osclients.session', mock_session2)
    def test_init_process_with_keystone_admin_endpoint_in_environment(self):
        """test_init_process_with_keystone_admin_endpoint_in_environment check that we
        could init the class with PasswordChanger with keystone defined in environment
        variable"""

        # Put the current variable in the environment.
        environ.setdefault('KEYSTONE_ADMIN_ENDPOINT', self.OS_KEYSTONE_ADMIN_ENDPOINT)

        passwordChanger = change_password.PasswordChanger()

        # Restore the setup value of the variable.
        del environ['KEYSTONE_ADMIN_ENDPOINT']

        expected_user_id = '00000000000000000000000000000001'

        self.assertTrue(passwordChanger.keystone is not None)
        self.assertEqual(passwordChanger.users_by_id[expected_user_id].cloud_project_id, expected_user_id)

    @patch('fiwareskuld.utils.osclients.session', mock_session3)
    def test_changepassword_exceptions(self):
        """ We test that we ctry to change password but when we request info,
        we get an error from kesytone.
        """
        with patch('__builtin__.open') as mocked_open:
            mocked_open.side_effect = self.side_effect_function

            passwordChanger = change_password.PasswordChanger()
            user = passwordChanger.get_user_byid(OS_TENANT_ID)

            try:
                passwordChanger.change_password(user, 'foo')
            except Exception as ex:
                self.assertEqual(ex.message, '404 No data received')

    @patch('fiwareskuld.utils.osclients.session', mock_session4)
    def test_changepassword_exceptions2(self):
        """ We test that we try to change password but when we try to patch
        we get an error.
        """
        with patch('__builtin__.open') as mocked_open:
            mocked_open.side_effect = self.side_effect_function

            passwordChanger = change_password.PasswordChanger()
            user = passwordChanger.get_user_byid(OS_TENANT_ID2)

            try:
                passwordChanger.change_password(user, 'foo')
            except Exception as ex:
                self.assertEqual(ex.message, '404 No PATCH')

    def side_effect_function(self, *args, **kwargs):
        """
        Get the corresponding resource data from the file, some users are not Basic
        but they has know tipe.
        :param args: path to the file to be loaded.
        :param kwargs: More arguments, in this case nothing important.
        :return: ContextualStringIO simulating that it is read from file.
        """

        if 'tests/units/resources/list_users_response.json' in args[0]:
            data = self.list_users_response
        elif 'tests/units/resources/get_user_response.json' in args[0]:
            data = self.get_users_response
        elif 'tests/units/resources/list_users_response4.json' in args[0]:
            data = self.list_users_response2
        else:
            data = NO_DATA

        return ContextualStringIO(data)
