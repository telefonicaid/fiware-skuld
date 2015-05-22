__author__ = 'fla'

import json
import requests
from datetime import datetime


class ExpiredUsers:
    def __init__(self):
        """ Initialize the class with the appropriate parameters.
        """
        self.TRIAL_ROLE_ID = "7698be72802342cdb2a78f89aa55d8ac"
        self.BASIC_ROLE_ID = "0bcb7fa6e85046cb9e89ded5656b192b"
        self.KEYSTONE_ENDPOINT = "http://cloud.lab.fiware.org:4730/"
        self.v20 = "v2.0/"
        self.v30 = "v3/"
        self.token = ""
        self.listUsers = []
        self.MAX_NUMBER_OF_DAYS = 14  # days
        self.finalList = []
        self.__tenant = ""
        self.__username = ""
        self.__password = ""

    def get_admin_token(self):
        """
        Return the admin token for a administrador user
        :return: The admin token to be used in the X-Auth-Token header
        """

        self.__check_credentials()

        payload = "{\"auth\":{\"tenantName\":\"%s\"," \
                  "\"passwordCredentials\":{\"username\":\"%s\",\"password\":\"%s\"}}}" \
                  % (self.__tenant, self.__username, self.__password)
        headers = {'content-type': 'application/json'}
        url = self.KEYSTONE_ENDPOINT + self.v20 + "tokens"
        r = requests.post(url=url, data=payload, headers=headers)

        rjson = json.loads(r.text)

        self.token = rjson['access']['token']['id']

        print "Admin token requested: " + self.token

    def get_list_trial_users(self):
        """
        Return the list of users which have the Trial Role defined
        :return: Lists of users id who have Trial role
        """
        self.__check_token()

        url = self.KEYSTONE_ENDPOINT + self.v30 + "role_assignments?role.id=" + self.TRIAL_ROLE_ID
        headers = {'X-Auth-Token': self.token}
        r = requests.get(url=url, headers=headers)

        role_assignments = json.loads(r.text)['role_assignments']

        # Extract the list of user_ids
        for item in role_assignments:
            self.listUsers.append(item['user']['id'])

        print "Number of Trial users detected: " + str(len(self.listUsers))

    def get_list_expired_users(self):
        """
        For each users id that have the Trial role, we need to check
        if the time from their creation (trial_created_at) have
        expired
        :return: Lists of Users id who have Trial role and expired
        """

        self.__check_token()

        url = self.KEYSTONE_ENDPOINT + self.v30 + "users/"
        headers = {'X-Auth-Token': self.token}

        # Extract the list of user_ids
        for user_id in self.listUsers:
            finalurl = url + user_id
            r = requests.get(url=finalurl, headers=headers)

            trial_started_at = json.loads(r.text)['user']['trial_started_at']

            if self.check_time(trial_started_at):
                # If true means that the user trial period has expired
                self.finalList.append(user_id)

        print len(self.finalList)
        return self.finalList

    def check_time(self, trial_started_at):

        formatter_string = "%Y-%m-%d"

        datetime_object = datetime.strptime(trial_started_at, formatter_string)
        date_object_old = datetime_object.date()

        datetime_object = datetime.today()
        date_object_new = datetime_object.date()

        difference = date_object_new - date_object_old

        if difference.days > self.MAX_NUMBER_OF_DAYS:
            result = True
        else:
            result = False

        return result

    def __check_token(self):
        """Check if the token is not blank"""
        if self.token == "":
            # We need to have a admin token in order to proceed.
            raise ValueError("Error, you need to have an admin token. Execute the get_admin_token() method previously.")

    def __check_credentials(self):
        """Check if we have the credentials of the admin user"""
        if self.__tenant == "" or self.__username == "" or self.__password == "":
            # We need to have a admin token in order to proceed.
            raise ValueError("Error, you need to define the credentials of the admin user. "
                             "Please, execute the setCredentials() method previously.")

    def getadmintoken(self):
        return self.token

    def gerlisttrialusers(self):
        return self.listUsers

    def set_credentials(self, tenant, username, password):
        self.__tenant = "tenant"
        self.__username = "username"
        self.__password = "password"
