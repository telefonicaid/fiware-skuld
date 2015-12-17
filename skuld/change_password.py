#!/usr/bin/env python
# -- encoding: utf-8 --
#
# Copyright 2015 Telefónica Investigación y Desarrollo, S.A.U
#
# This file is part of FI-Core project.
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
#


import argparse
import base64

from utils import osclients
import os

class PasswordChanger(object):
    """Class to change/reset the password of any user"""
    def __init__(self, osclients_o=None):
        """constructor of the object. It receives the environment variables with
        the admin credential"""

        if not osclients_o:
            osclients_o = osclients.OpenStackClients()

        if 'KEYSTONE_ADMIN_ENDPOINT' in os.environ:
            osclients_o.override_endpoint(
                'identity', osclients_o.region, 'admin',
                os.environ['KEYSTONE_ADMIN_ENDPOINT'])

        self.keystone = osclients_o.get_keystoneclient()
        self.users_by_id = dict()
        for user in self.keystone.users.list():
            self.users_by_id[user.id] = user

    def change_password(self, userobj, newpassword):
        """
        change the password of the user.
        :param userobj: a user, this object may be obtained with get_userbyid
          or get_userbyname methods
        :param newpassword: the new password
        :return: Nothing
        """
        userid = userobj.id
        (resp, user) = self.keystone.users.client.get('/users/' + userid)
        if not resp.ok:
            raise Exception(str(resp.status_code) + ' ' + resp.reason)
        user['user']['password'] = newpassword
        (resp, user) = self.keystone.users.client.patch('/users/' + userid,
                                                        body=user)
        if not resp.ok:
            raise Exception(str(resp.status_code) + ' ' + resp.reason)

    def reset_password(self, userobj):
        """
        Set a new, random password and return it.

        The password length is 21 characters, it may contain a-zA-Z0-9!. It is
        the equivalent to a 128 bits key.

        :param userobj: a user, this object may be obtained with get_userbyid
          or get_userbyname methods
        :return: the new password
        """
        rand = open('/dev/urandom')
        password = base64.b64encode(rand.read(16), '.!')[:21]
        self.change_password(userobj, password)
        return password

    def get_user_byid(self, userid):
        """
        Return a user object from its userid. This object may be used with
         methods change_password and reset_password
        :param userid: the UUID of the user
        :return: a user object
        """
        # Does not work:
        #   return self.keystone.users.find(id=userid)
        return self.users_by_id[userid]

    def get_user_byname(self, username):
        """
        Return a user object from its username. This object may be used with
         methods change_password and reset_password
        :param username: the UUID of the user
        :return: a user object
        """
        return self.keystone.users.find(name=username)

    def get_list_users_with_cred(self, list_user_ids):
        """This method from a list of user ids, reset the password and returns
        a list with the username, new password, and tenant. This information is
        enough to authenticate as the user

        :param list_user_ids: a list of user ids
        :return: a list of tuples, with (username, password, tenant_id)
        """
        list_creds = list()
        for user_id in list_user_ids:
            userobj = self.get_user_byid(user_id)
            password = self.reset_password(userobj)
            cred = (userobj.name, password, userobj.default_project_id)
            list_creds.append(cred)
        return list_creds

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Change a user's password")
    parser.add_argument('username')
    parser.add_argument('newpassword')
    meta = parser.parse_args()
    manager = PasswordChanger()
    usr = manager.get_user_byname(meta.username)
    manager.change_password(usr, meta.newpassword)
