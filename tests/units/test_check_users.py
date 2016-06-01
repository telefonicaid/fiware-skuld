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
    LIST_USERS_RESPONSE_FILE3
from httplib import OK
from os import environ
import os
from StringIO import StringIO
from collections import defaultdict

OS_TENANT_ID = '00000000000000000000000000000001'


class MySessionMock(MagicMock):
    # Mock of a keystone Session

    def get_endpoint(self, **kwargs):

        endpoint = "http://cloud.host.fi-ware.org:4731/v2.0"
        return endpoint

    def get_access(self, session):

        service2 = {u'endpoints': [{u'url': u'http://83.26.10.2:4730/v3/',
                                    u'interface': u'public', u'region': u'Spain2',
                                    u'id': u'00000000000000000000000000000002'},
                                   {u'url': u'http://172.0.0.1:4731/v3/', u'interface': u'administator',
                                    u'region': u'Spain2', u'id': u'00000000000000000000000000000001'
                                    }
                                   ],
                    u'type': u'identity', u'id': u'00000000000000000000000000000045'}

        d = defaultdict(list)
        d['catalog'].append(service2)

        return d

    def get_token(self):
        """return a token"""
        return "a12baba1ddde00000000000000000001"

    def request(self, url, method, **kwargs):

        resp = Response()

        if url == '/role_assignments?scope.domain.id=default':
            json_data = open(UNIT_TEST_RESOURCES_FOLDER + LIST_ROLE_ASSIGNMENTS_RESPONSE_FILE_EXTENDED1).read()
            resp.status_code = OK
            resp._content = json_data
        elif url == '/role_assignments?user.id=fake3&scope.domain.id=default':
            json_data = open(UNIT_TEST_RESOURCES_FOLDER + LIST_USERS_RESPONSE_FILE2).read()
            resp.status_code = OK
            resp._content = json_data
        return resp


class ContextualStringIO(StringIO):
    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()  # icecrime does it, so I guess I should, too
        return False  # Indicate that we haven't handled the exception, if received

    def __getitem__(self, item):
        return self.__getitem__(item)


class TestCheckUsers(TestCase):
    mock_session = MySessionMock()

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

    def tearDown(self):
        if 'KEYSTONE_ADMIN_ENDPOINT' in os.environ:
            del os.environ['KEYSTONE_ADMIN_ENDPOINT']

    def side_effect_function(self, *args, **kwargs):
        if 'users_to_delete.txt' in args[0]:
            data = self.list_user_to_delete
        elif 'list_role_assignments_response1.json' in args[0]:
            data = self.list_role_assignment1
        elif 'list_users_response2.json' in args[0]:
            data = self.list_users_response2
        else:
            data = 'No data'

        return ContextualStringIO(data)

    def side_effect_function2(self, *args, **kwargs):
        if 'users_to_delete.txt' in args[0]:
            data = self.list_user_to_delete
        elif 'list_role_assignments_response1.json' in args[0]:
            data = self.list_role_assignment1
        elif 'list_users_response3.json' in args[0]:
            data = self.list_users_response3
        else:
            data = 'No data'

        return ContextualStringIO(data)

    def side_effect_function3(self, *args, **kwargs):
        if 'users_to_delete.txt' in args[0]:
            data = self.list_user_to_delete
        elif 'list_role_assignments_response1.json' in args[0]:
            data = self.list_role_assignment2
        elif 'list_users_response3.json' in args[0]:
            data = self.list_users_response3
        else:
            data = 'No data'

        return ContextualStringIO(data)

    @patch('fiwareskuld.utils.osclients.session', mock_session)
    def test_check_user_init(self):
        from fiwareskuld.check_users import CheckUsers

        expectedUserSet = set(['fake1', 'fake2', 'fake3'])
        expectedUserBasicSet = set([u'fake1', u'fake2'])

        with patch('__builtin__.open') as mocked_open:
            mocked_open.side_effect = self.side_effect_function

            check = CheckUsers()

            self.assertSetEqual(expectedUserSet, check.ids,
                                "Unexpected content in users_to_delete file")

            self.assertSetEqual(expectedUserBasicSet, check.users_basic,
                                "The expected users with Basic role is not obtained")

    @patch('fiwareskuld.utils.osclients.session', mock_session)
    def test_report_not_basic_users(self):
        from fiwareskuld.check_users import CheckUsers

        expectedUserSet = set(['fake3'])
        expectedUserTypeSet = set(['community'])

        with patch('__builtin__.open') as mocked_open:
            mocked_open.side_effect = self.side_effect_function

            check = CheckUsers()

            no_basic_users, no_basic_userstype = check.report_not_basic_users()

            self.assertSetEqual(expectedUserSet, no_basic_users,
                                "The expected set of no basic users is wrong")

            self.assertSetEqual(expectedUserTypeSet, no_basic_userstype,
                                "The expected set of type of no basic users is wrong")

    @patch('fiwareskuld.utils.osclients.session', mock_session)
    def test_report_invalid_users_type(self):
        from fiwareskuld.check_users import CheckUsers

        expectedUserSet = set(['fake3'])
        expectedUserTypeSet = set(['unkown'])

        with patch('__builtin__.open') as mocked_open:
            mocked_open.side_effect = self.side_effect_function2

            check = CheckUsers()

            no_basic_users, no_basic_userstype = check.report_not_basic_users()

            self.assertSetEqual(expectedUserSet, no_basic_users,
                                "The expected set of no basic users is wrong")

            self.assertSetEqual(expectedUserTypeSet, no_basic_userstype,
                                "The expected set of type of no basic users is wrong")

    @patch('fiwareskuld.utils.osclients.session', mock_session)
    def test_report_all_users_basic(self):
        from fiwareskuld.check_users import CheckUsers

        expectedUserSet = set([])
        expectedUserTypeSet = set([])

        with patch('__builtin__.open') as mocked_open:
            mocked_open.side_effect = self.side_effect_function3

            check = CheckUsers()

            no_basic_users, no_basic_userstype = check.report_not_basic_users()

            self.assertSetEqual(expectedUserSet, no_basic_users,
                                "The expected set of no basic users is wrong")

            self.assertSetEqual(expectedUserTypeSet, no_basic_userstype,
                                "The expected set of type of no basic users is wrong")
