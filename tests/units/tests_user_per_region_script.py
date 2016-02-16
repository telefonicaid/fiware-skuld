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
from scripts.userListPerRegion import users
import os

__author__ = 'fla'


@requests_mock.Mocker()
class TestChangePassword(TestCase):
    def test_gettoken(self, m):
        """
        Test the response of a valid token.

        :param m: The request mocker
        :return: Nothing
        """
        # Given
        response = {'access': {'token': {'id': '49ede5a9ce224631bc778cceedc0cca1'}}}
        expectedToken = '49ede5a9ce224631bc778cceedc0cca1'

        m.post(requests_mock.ANY, json=response)

        # When
        resultToken = users.get_token(username='fake user', password='a fake password')

        # Then
        self.assertEqual(expectedToken, resultToken)

    def test_getregionid(self, m):
        """
        Test the obtention of a corresponding id of the region to check.

        :param m: The request mocker
        :return: Nothing
        """
        # Given
        response = {
            "endpoint_groups": [
                {
                    "id": "000bd9fe677544829dd6659d1af7713b",
                    "filters": {
                        "region_id": "Trento"
                    }
                },
                {
                    "id": "00a2a9c70620449aab5bba4ca3e6349e",
                    "filters": {
                    "region_id": "Budapest2"
                    }
                },
                {
                    "id": "09289e15b2bb4a4a85df1550b4f8c936",
                    "filters": {
                        "region_id": "Stockholm2"
                    }
                }
            ],
        }

        expectedResult = '000bd9fe677544829dd6659d1af7713b'

        url = os.path.join(users.KEYSTONE_URL, users.API_V3, users.ENDPOINT_GROUPS)

        m.get(url, json=response)

        # When
        resultRegionId = users.get_endpoint_groups_id(token='a fake token', region='Trento')

        # Then
        self.assertEqual(expectedResult, resultRegionId)

    def test_getprojectlist(self, m):
        """
        Test the request to obtain the list of projects in a specific region.

        :param m: The request mocker
        :return: Nothing
        """
        # Given
        response = {
            "projects": [
                {
                    "id": "00000000000000000000000000000043",
                },
                {
                    "id": "00000000000000000000000000000081",
                },
                {
                    "id": "00000000000000000000000000000082",
                },
            ]
        }

        expectedResult = [
            '00000000000000000000000000000043',
            '00000000000000000000000000000081',
            '00000000000000000000000000000082'
        ]

        regionid = '000bd9fe677544829dd6659d1af7713b'
        project_details = users.PROJECT_DETAILS % regionid
        url = os.path.join(users.KEYSTONE_URL, users.API_V3, users.ENDPOINT_GROUPS, project_details)

        m.get(url, json=response)

        # When
        resultProjects = users.get_project_list(token='a fake token', regionid='000bd9fe677544829dd6659d1af7713b')

        # Then
        self.assertEqual(expectedResult, resultProjects)

    def test_getuserlist(self, m):
        """
        Test the obtention of the different user with some role in the region.

        :param m: The request mocker
        :return: Nothing
        """
        # Given
        response1 = {
            "role_assignments": [
                {
                    "user": {
                        "id": "alvaro-alonso"
                    },
                },
                {
                    "user": {
                        "id": "alvaro-test"
                    },
                }
            ],
            "links": {
                "self": "fake url",
            }
        }

        response2 = {
            "role_assignments": [
                {
                    "user": {
                        "id": "alvaro-alonso"
                    },
                },
                {
                    "user": {
                        "id": "federico-facca"
                    },
                }
            ],
            "links": {
                "self": "fake url",
            }
        }

        expectedResult = {'alvaro-alonso', 'alvaro-test', 'federico-facca'}

        projectlist = ['1', '2']

        response = {
            '1': response1,
            '2': response2
        }

        for i in projectlist:
            role_assignment = users.ROLE_ASSIGNMENT % i
            url = os.path.join(users.KEYSTONE_URL, users.API_V3, role_assignment)

            m.get(url, json=response[i])

        # When
        resultUsersList = users.get_user_list(token='a fake token', projectlist=projectlist)

        # Then
        self.assertEqual(expectedResult, resultUsersList)

    def test_getemail(self, m):
        """
        Test the obtention of a dictionary with the user name and user email.

        :param m: The request mocker
        :return: Nothing
        """
        # Given
        userset = {'alvaro-alonso', 'alvaro-test', 'federico-facca'}

        expectedResult = {
            'alvaro-alonso': 'foo@foo.es',
            'alvaro-test': 'spain@fiware.org',
            'federico-facca': 'fake@fake.com'
        }

        response = {
            "users": [
                {
                    "name": "foo@foo.es",
                    "id": "alvaro-alonso",
                },
                {
                    "name": "spain@fiware.org",
                    "id": "alvaro-test",
                },
                {
                    "name": "fake@fake.com",
                    "id": "federico-facca",
                }
            ]
        }

        url = os.path.join(users.KEYSTONE_URL, users.API_V3, users.USER_DETAILS)

        m.get(url, json=response)

        # When
        resultEmails = users.get_email(token='a fake token', userset=userset)

        # Then
        self.assertEqual(expectedResult, resultEmails)
