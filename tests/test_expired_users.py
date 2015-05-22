__author__ = 'fla'

from unittest import TestCase
from expired_users import ExpiredUsers
from datetime import datetime
import requests_mock
import re

@requests_mock.Mocker()
class TestExpiredUsers(TestCase):
    def testadmintoken(self, m):
        """testadmintoken check that we have an admin token"""
        response = {'access': {'token': {'id': '49ede5a9ce224631bc778cceedc0cca1'}}}

        m.post(requests_mock.ANY, json=response)

        expiredUsers = ExpiredUsers()

        expiredUsers.set_credentials('any tenant id', 'any username', 'any password')
        expiredUsers.get_admin_token()

        resultToken = expiredUsers.getadmintoken()
        expectedToken = "49ede5a9ce224631bc778cceedc0cca1"

        self.assertEqual(expectedToken, resultToken)

    def testadmintokenWithoutCredentials(self, m):
        """Test the obtention of admin token withput credentials"""
        expiredUsers = ExpiredUsers()

        expectedmessage = 'Error, you need to define the credentials of the admin user. ' \
                          'Please, execute the setCredentials() method previously.'

        try:
            expiredUsers.get_admin_token()
        except ValueError as e:
            self.assertEqual(e.message, expectedmessage)


    def testlistTrialUsers(self, m):
        """testadmintoken check that we have an admin token"""
        response = {"role_assignments": [
                     {
                      "user": {"id": "0f4de1ea94d342e696f3f61320c15253"},
                      "links": {"assignment": "http://aurl.com/abc"}
                     },
                     {
                      "user": {"id": "24396976a1b84eafa5347c3f9818a66a"},
                      "links": {"assignment": "http://a.com"}
                     },
                     {
                      "user": {"id": "24cebaa9b665426cbeab579f1a3ac733"},
                      "links": {"assignment": "http://b.com"}
                     },
                     {
                      "user": {"id": "zippitelli"},
                      "links": {"assignment": "http://c.com"}
                     }],
                     "links": {"self": "http://d.com"}
        }

        m.get(requests_mock.ANY, json=response)

        expiredusers = ExpiredUsers()

        expiredusers.token = 'a token'
        expiredusers.get_list_trial_users()

        result = expiredusers.gerlisttrialusers()

        expectedresult = ['0f4de1ea94d342e696f3f61320c15253', '24396976a1b84eafa5347c3f9818a66a',
                          '24cebaa9b665426cbeab579f1a3ac733', 'zippitelli']

        self.assertEqual(expectedresult, result)

    def testlistTrialUsersWithNoAdminToken(self, m):
        """testlistTrialUsersWithNoAdminToken check that we have an admin token"""
        expiredusers = ExpiredUsers()

        #There was no users in the list
        expiredusers.token = ""
        expectedmessage = "Error, you need to have an admin token. Execute the get_admin_token() method previously."

        try:
            result = expiredusers.get_list_trial_users()
        except ValueError as e:
            self.assertEqual(e.message, expectedmessage)

    def testCheckTimeExpired(self, m):
        """testadmintoken check that we have an admin token"""
        m.get(requests_mock.ANY, json=self.text_callback)

        expiredusers = ExpiredUsers()
        expiredusers.token = 'a token'
        expiredusers.listUsers = ['0f4de1ea94d342e696f3f61320c15253', '24396976a1b84eafa5347c3f9818a66a']

        result = expiredusers.get_list_expired_users()

        expectedresult = ['24396976a1b84eafa5347c3f9818a66a']

        self.assertEqual(expectedresult, result)

    def text_callback(self, request, context):
        """
        Create the returns message of the request based on the information that we request.
        :param request: The request send to the server
        :param context: The context send to the server
        :return: The message to be returned in the requests.
        """
        # Create the dictionary with the possible values.
        result1 = {
                   "user": {
                       "username": "Rodo",
                       "cloud_project_id": "8f1d82b3a20f403a823954423fd8f451",
                       "name": "rododendrotiralapiedra@hotmail.com",
                       "links": {"self": "http://cloud.lab.fiware.org:4730/v3/users/0f4de1ea94d342e696f3f61320c15253"},
                       "enabled": True,
                       "trial_started_at": "2015-05-10",
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
                       "links": {"self": "http://cloud.lab.fiware.org:4730/v3/users/0f4de1ea94d342e696f3f61320c15253"},
                       "enabled": True,
                       "trial_started_at": "2015-04-10",
                       "domain_id": "default",
                       "default_project_id": "e29eff7c153b448caf684aa9031d01c6",
                       "id": "24396976a1b84eafa5347c3f9818a66a"
                   }
        }

        result = { '0f4de1ea94d342e696f3f61320c15253': result1, "24396976a1b84eafa5347c3f9818a66a": result2}

        #extract the user_id from the request.path content
        matchObj = re.match( r'/v3/users/(.*)', request.path, re.M|re.I)

        return result[matchObj.group(1)]

    def testCheckTimeExpiredwithNoListUsers(self, m):
        """testadmintoken check that we have an admin token"""

        expiredusers = ExpiredUsers()

        #There was no users in the list
        expiredusers.listUsers = []
        expiredusers.token = 'a token'

        result = expiredusers.get_list_expired_users()

        expectedresult = []

        self.assertEqual(expectedresult, result)

    def testCheckTimeExpiredwithNoAdminToken(self, m):
        """testadmintoken check that we have an admin token"""
        expiredusers = ExpiredUsers()

        #There was no users in the list
        expiredusers.token = ""
        expectedmessage = "Error, you need to have an admin token. Execute the get_admin_token() method previously."

        try:
            result = expiredusers.get_list_expired_users()
        except ValueError as e:
            self.assertEqual(e.message, expectedmessage)

    def testcheckTime1(self, m):
        """ test the difference between two dates in string are bigger than 14 days."""
        expiredusers = ExpiredUsers()

        olddate = "2015-05-01"

        result = expiredusers.check_time(olddate)

        expectedresult = True

        self.assertEqual(expectedresult, result)

    def testcheckTime2(self, m):
        """ test the difference between two dates in string are bigger than 14 days."""
        expiredusers = ExpiredUsers()

        aux = datetime.today()
        olddate = aux.strftime("%Y-%m-%d")

        result = expiredusers.check_time(olddate)

        expectedresult = False

        self.assertEqual(expectedresult, result)
