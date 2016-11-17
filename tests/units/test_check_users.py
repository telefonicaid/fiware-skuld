# -*- coding: utf-8 -*-

# Copyright 2015-2016 Telefónica Investigación y Desarrollo, S.A.U
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

from mock import patch, MagicMock
from unittest import TestCase
from requests import Response
from tests_constants import UNIT_TEST_RESOURCES_FOLDER, LIST_ROLE_ASSIGNMENTS_RESPONSE_FILE_EXTENDED1, \
    LIST_ROLE_ASSIGNMENTS_RESPONSE_FILE_EXTENDED2, LIST_USERS_TO_DELETE, LIST_USERS_RESPONSE_FILE2, \
    LIST_USERS_RESPONSE_FILE3, NO_DATA, LIST_ROLES_COMMUNITY_RESPONSE_FILE, LIST_ROLES_ID_BASIC_RESPONSE_FILE, \
    LIST_ROLE_ASSIGNMENTS_TRIAL_RESPONSE_FILE, LIST_ROLES_BASIC_RESPONSE_FILE, LIST_ROLES_TRIAL_RESPONSE_FILE, \
    LIST_ROLE_ASSIGNMENTS_RESPONSE_FILE, ROLE_TRIAL_RESPONSE_FILE
from httplib import OK
from os import environ
import os
from StringIO import StringIO
from collections import defaultdict

OS_TENANT_ID = '00000000000000000000000000000001'


class ContextualStringIO(StringIO):
    # Extend StringIO class to get __enter__, __exit__ and __getitem__ methods.

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
        return False  # Indicate that we haven't handled the exception, if received

    def __getitem__(self, item):
        return self.__getitem__(item)


class TestCheckUsers(TestCase):
    import test_openstackmap
    mock_session = test_openstackmap.MySessionMock()

    def setUp(self):
        self.OS_AUTH_URL = 'http://cloud.host.fi-ware.org:4731/v2.0'
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

        self.list_user_to_delete = open(UNIT_TEST_RESOURCES_FOLDER + LIST_USERS_TO_DELETE).read()

        self.list_role_assignment1 = \
            open(UNIT_TEST_RESOURCES_FOLDER + LIST_ROLE_ASSIGNMENTS_RESPONSE_FILE_EXTENDED1).read()

        self.list_role_assignment2 = \
            open(UNIT_TEST_RESOURCES_FOLDER + LIST_ROLE_ASSIGNMENTS_RESPONSE_FILE_EXTENDED2).read()

        self.list_users_response2 = open(UNIT_TEST_RESOURCES_FOLDER + LIST_USERS_RESPONSE_FILE2).read()

        self.list_users_response3 = open(UNIT_TEST_RESOURCES_FOLDER + LIST_USERS_RESPONSE_FILE3).read()
        self.list_role_community = open(UNIT_TEST_RESOURCES_FOLDER + LIST_ROLES_COMMUNITY_RESPONSE_FILE).read()
        self.list_role_basic = open(UNIT_TEST_RESOURCES_FOLDER + LIST_ROLES_ID_BASIC_RESPONSE_FILE).read()
        self.list_role = open(UNIT_TEST_RESOURCES_FOLDER + LIST_ROLE_ASSIGNMENTS_TRIAL_RESPONSE_FILE).read()
        self.list_basic_assigment = open(UNIT_TEST_RESOURCES_FOLDER + LIST_ROLES_BASIC_RESPONSE_FILE).read()
        self.list_role_assigment = open(UNIT_TEST_RESOURCES_FOLDER + LIST_ROLE_ASSIGNMENTS_RESPONSE_FILE).read()
        self.trial_roles = open(UNIT_TEST_RESOURCES_FOLDER + LIST_ROLES_TRIAL_RESPONSE_FILE).read()
        self.trial_role = open(UNIT_TEST_RESOURCES_FOLDER + ROLE_TRIAL_RESPONSE_FILE).read()

    def tearDown(self):
        if 'KEYSTONE_ADMIN_ENDPOINT' in os.environ:
            del os.environ['KEYSTONE_ADMIN_ENDPOINT']

    def side_effect_function(self, *args, **kwargs):
        """
        Get the corresponding resource data from the file, some users are not Basic
        but they has know tipe.
        :param args:
        :param kwargs: More arguments, in this case nothing important.
        :return: ContextualStringIO simulating that it is read from file.
        """

        if LIST_USERS_TO_DELETE in args[0]:
            data = self.list_user_to_delete
        elif LIST_ROLE_ASSIGNMENTS_RESPONSE_FILE_EXTENDED1 in args[0]:
            data = self.list_role_assignment1
        elif LIST_USERS_RESPONSE_FILE2 in args[0]:
            data = self.list_users_response2
        elif LIST_ROLES_COMMUNITY_RESPONSE_FILE in args[0]:
            data = self.list_role_community
        elif LIST_ROLES_ID_BASIC_RESPONSE_FILE in args[0]:
            data = self.list_role_basic
        elif LIST_ROLE_ASSIGNMENTS_TRIAL_RESPONSE_FILE in args[0]:
            data = self.list_role
        elif LIST_ROLES_BASIC_RESPONSE_FILE in args[0]:
            data = self.list_role_basic
        elif LIST_ROLE_ASSIGNMENTS_RESPONSE_FILE in args[0]:
            data = self.list_role_assigment
        elif LIST_ROLES_TRIAL_RESPONSE_FILE in args[0]:
            data = self.trial_roles
        elif ROLE_TRIAL_RESPONSE_FILE in args[0]:
            data = self.trial_role
        else:
            data = NO_DATA
        return ContextualStringIO(data)

    @patch('fiwareskuld.utils.osclients.session', mock_session)
    def test_check_user_init(self):
        from fiwareskuld.check_users import CheckUsers

        expectedUserSet = {'user_basic1', 'user_trial1', 'fake'}
        expectedUserBasicSet = {u'user_basic1'}

        with patch('__builtin__.open') as mocked_open:
            mocked_open.side_effect = self.side_effect_function

            check = CheckUsers()
            check.get_ids()

            self.assertSetEqual(expectedUserSet, check.ids,
                                "Unexpected content in users_to_delete file")

            self.assertSetEqual(expectedUserBasicSet, check.users_basic,
                                "The expected users with Basic role is not obtained")

            self.assertTrue(mocked_open.called)

    @patch('fiwareskuld.utils.osclients.session', mock_session)
    def test_report_all_users_basic(self):
        from fiwareskuld.check_users import CheckUsers

        expectedUserSet = {"user_trial1", "fake"}
        expectedUserTypeSet = {"trial", "unkown"}

        with patch('__builtin__.open') as mocked_open:
            mocked_open.side_effect = self.side_effect_function

            check = CheckUsers()
            check.get_ids()
            no_basic_users, no_basic_userstype = check.report_not_basic_users()

            self.assertSetEqual(expectedUserSet, no_basic_users,
                                "The expected set of no basic users is wrong")

            self.assertSetEqual(expectedUserTypeSet, no_basic_userstype,
                                "The expected set of type of no basic users is wrong")

            self.assertTrue(mocked_open.called)
