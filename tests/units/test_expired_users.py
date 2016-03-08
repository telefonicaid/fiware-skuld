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
from datetime import datetime, timedelta
import re
import requests_mock
from fiwareskuld.expired_users import ExpiredUsers


@requests_mock.Mocker()
class TestExpiredUsers(TestCase):
    def testadmintoken(self, m):
        """testadmintoken check that we have an admin token"""
        response = {'access': {'token': {'id': '49ede5a9ce224631bc778cceedc0cca1'}}}

        m.post(requests_mock.ANY, json=response)

        expiredUsers = ExpiredUsers('any tenant id', 'any username', 'any password')

        expiredUsers.get_admin_token()

        resultToken = expiredUsers.getadmintoken()
        expectedToken = "49ede5a9ce224631bc778cceedc0cca1"

        self.assertEqual(expectedToken, resultToken)

    def testwrongadmintoken(self, m):
        """testworngadmintoken check that we have a worg credential data"""
        response = {
            "error":
                {
                    "message": "The request you have made requires authentication.",
                    "code": 401,
                    "title": "Unauthorized"
                }
        }

        m.post(requests_mock.ANY, json=response, status_code=401)

        expiredUsers = ExpiredUsers('wrong tenant', 'any username', 'any password')

        try:
            expiredUsers.get_admin_token()
        except Exception as e:

            assert e.message == 'The request you have made requires authentication.'

    def testadmintokenWithoutCredentials(self, m):
        """Test the obtention of admin token without credentials"""
        expiredUsers = ExpiredUsers()

        expectedmessage = 'Error, you need to define the credentials of the admin user. ' \
                          'Please, execute the setCredentials() method previously.'

        try:
            expiredUsers.get_admin_token()
        except ValueError as e:
            self.assertEqual(e.message, expectedmessage)

    def testlistTrialUsers(self, m):
        """testadmintoken check that we have an admin token"""
        response = {
            "role_assignments": [
                {"user": {"id": "0f4de1ea94d342e696f3f61320c15253"}, "links": {"assignment": "http://aurl.com/abc"}
                 },
                {"user": {"id": "24396976a1b84eafa5347c3f9818a66a"}, "links": {"assignment": "http://a.com"}
                 },
                {"user": {"id": "24cebaa9b665426cbeab579f1a3ac733"}, "links": {"assignment": "http://b.com"}
                 },
                {"user": {"id": "zippitelli"}, "links": {"assignment": "http://c.com"}
                 }
            ],
            "links": {"self": "http://d.com"}
        }

        m.get(requests_mock.ANY, json=response)

        expiredusers = ExpiredUsers('any tenant id', 'any username', 'any password')

        expiredusers.token = 'a token'
        expiredusers.get_list_trial_users()

        result = expiredusers.gerlisttrialusers()

        expectedresult = ['0f4de1ea94d342e696f3f61320c15253', '24396976a1b84eafa5347c3f9818a66a',
                          '24cebaa9b665426cbeab579f1a3ac733', 'zippitelli']

        self.assertEqual(expectedresult, result)

    def testlistTrialUsersWithNoAdminToken(self, m):
        """testlistTrialUsersWithNoAdminToken check that we have an admin token"""
        expiredusers = ExpiredUsers('any tenant id', 'any username', 'any password')

        # There was no users in the list
        expiredusers.token = ""
        expectedmessage = "Error, you need to have an admin token. Execute the get_admin_token() method previously."

        try:
            expiredusers.get_list_trial_users()
        except ValueError as e:
            self.assertEqual(e.message, expectedmessage)

    def testCheckTimeExpired(self, m):
        """testadmintoken check that we have an admin token"""
        m.get(requests_mock.ANY, json=self.text_callback)

        expiredusers = ExpiredUsers('any tenant id', 'any username', 'any password')
        expiredusers.token = 'a token'
        expiredusers.listUsers = ['0f4de1ea94d342e696f3f61320c15253',
                                  '24396976a1b84eafa5347c3f9818a66a',
                                  'e3294fcf05984b3f934e189fa92c6990']

        result = expiredusers.get_list_expired_users()

        expectedresult = ['24396976a1b84eafa5347c3f9818a66a', 'e3294fcf05984b3f934e189fa92c6990']

        self.assertEqual(expectedresult, result)

    def testCheckTimeExpiredWithNoUsers(self, m):
        """testCheckTimeExpiredWithNoUsers check that we receive an error if we do not execute the
        get_list_trial_users() previously"""
        m.get(requests_mock.ANY, json=self.text_callback)

        expiredusers = ExpiredUsers('any tenant id', 'any username', 'any password')
        expiredusers.token = 'a token'

        result = expiredusers.get_list_expired_users()

        expectedresult = []

        self.assertEqual(expectedresult, result)

    def text_callback(self, request, context):
        """
        Create the returns message of the request based on the information that we request.
        :param request: The request send to the server
        :param context: The context send to the server
        :return: The message to be returned in the requests.
        """
        datetime_value1 = (datetime.now() + timedelta(days=-10)).date()  # Here, I am adding a negative timedelta
        datetime_value2 = (datetime.now() + timedelta(days=-20)).date()  # Here, I am adding a negative timedelta

        # Create the dictionary with the possible values.
        result1 = {
            "user": {
                "username": "Rodo",
                "cloud_project_id": "8f1d82b3a20f403a823954423fd8f451",
                "name": "rododendrotiralapiedra@hotmail.com",
                "links": {"self": "http://cloud.lab.fiware.org:4730/v3/users/0f4de1ea94d342e696f3f61320c15253"},
                "enabled": True,
                "trial_started_at": str(datetime_value1),
                "domain_id": "default",
                "default_project_id": "e29eff7c153b448caf684aa9031d01c6",
                "id": "0f4de1ea94d342e696f3f61320c15253"
            }
        }

        result2 = {
            "user": {
                "username": "Rodo",
                "cloud_project_id": "8f1d82b3a20f403a823954423fd8f451",
                "name": "rododendrotiralapiedra@hotmail.com",
                "links": {"self": "http://cloud.lab.fiware.org:4730/v3/users/24396976a1b84eafa5347c3f9818a66a"},
                "enabled": True,
                "trial_started_at": str(datetime_value2),
                "domain_id": "default",
                "default_project_id": "e29eff7c153b448caf684aa9031d01c6",
                "id": "24396976a1b84eafa5347c3f9818a66a"
            }
        }

        result3 = {
            "user": {
                "username": "Frodo",
                "cloud_project_id": "8f1d82b3a20f403a823954423fd8f451",
                "name": "frodobolsom@hotmail.com",
                "links": {"self": "http://cloud.lab.fiware.org:4730/v3/users/e3294fcf05984b3f934e189fa92c6990"},
                "enabled": True,
                "trial_started_at": str(datetime_value2),
                "domain_id": "default",
                "default_project_id": "e29eff7c153b448caf684aa9031d01c6",
                "id": "e3294fcf05984b3f934e189fa92c6990"
            }
        }

        result = {
            "0f4de1ea94d342e696f3f61320c15253": result1,
            "24396976a1b84eafa5347c3f9818a66a": result2,
            "e3294fcf05984b3f934e189fa92c6990": result3
        }

        # Extract the user_id from the request.path content
        matchObj = re.match(r'/v3/users/(.*)', request.path, re.M | re.I)

        return result[matchObj.group(1)]

    def testCheckTimeExpiredwithNoListUsers(self, m):
        """testadmintoken check that we have an admin token"""

        expiredusers = ExpiredUsers('any tenant id', 'any username', 'any password')

        # There was no users in the list
        expiredusers.listUsers = []
        expiredusers.token = 'a token'

        result = expiredusers.get_list_expired_users()

        expectedresult = []

        self.assertEqual(expectedresult, result)

    def testCheckTimeExpiredwithNoAdminToken(self, m):
        """testadmintoken check that we have an admin token"""
        expiredusers = ExpiredUsers('any tenant id', 'any username', 'any password')

        # There was no users in the list
        expiredusers.token = ""
        expectedmessage = "Error, you need to have an admin token. Execute the get_admin_token() method previously."

        try:
            expiredusers.get_list_expired_users()
        except ValueError as e:
            self.assertEqual(e.message, expectedmessage)

    def testcheckTime1(self, m):
        """ test the difference between two dates in string are bigger than 14 days."""
        expiredusers = ExpiredUsers('any tenant id', 'any username', 'any password')

        olddate = "2015-05-01"

        result = expiredusers.check_time(olddate)

        expectedresult = True

        self.assertEqual(expectedresult, result)

    def testcheckTime2(self, m):
        """ test the difference between two dates in string are bigger than 14 days."""
        expiredusers = ExpiredUsers('any tenant id', 'any username', 'any password')

        aux = datetime.today()
        olddate = aux.strftime("%Y-%m-%d")

        result = expiredusers.check_time(olddate)

        expectedresult = False

        self.assertEqual(expectedresult, result)

    def testkeystonegetter(self, m):
        """ Test the obtention of appropriate value of the Keystone service endpoint.
        """
        expiredusers = ExpiredUsers()

        result = expiredusers.get_keystone_endpoint()

        expectedresult = "http://cloud.lab.fiware.org:4730/"

        self.assertEqual(expectedresult, result)

    def testkeystonesetter(self, m):
        """ Test the setter method to fis the Keystone service endpoint
        """
        expiredusers = ExpiredUsers()

        expectedresult = "any url"

        expiredusers.set_keystone_endpoint(expectedresult)

        result = expiredusers.get_keystone_endpoint()

        self.assertEqual(expectedresult, result)
