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


import datetime

from fiwareskuld.conf import settings
from fiwareskuld.utils import osclients
from fiwareskuld.expired_users import ExpiredUsers
from os import environ


class CreateUser(object):
    """Class to generate users."""
    def __init__(self):
        """constructor"""
        clients = osclients.OpenStackClients()
        clients.override_endpoint(
            'identity', clients.region, 'admin', settings.KEYSTONE_ENDPOINT)
        self.nova_c = clients.get_novaclient()
        self.neutron_c = clients.get_neutronclient()
        self.keystone = clients.get_keystoneclientv3()
        self.exp = ExpiredUsers()

    def add_domain_user_role(self, user, role, domain):
        """ It adds a role to a user.
        :param user: the user
        :param role: the role to add
        :param domain: the domain
        :return: nothing
        """
        manager = self.keystone.roles
        return manager.grant(role, user=user, domain=domain)

    def update_domain_to_role(self, user, role_name, date_now=None, duration=100):
        """
        It updates the domain to the role
        :param user: the user
        :param role_name: the role
        :param duration: the duration for community
        :return: nothing
        """
        role = self.keystone.roles.find(name=role_name)

        if date_now:
            date_out = str(date_now)
        else:
            date_out = str(datetime.date.today())

        if role_name == "community":
            self.keystone.users.update(user, community_started_at=date_out, community_duration=duration)
        elif role_name == "trial":
            self.keystone.users.update(user, trial_started_at=date_out)

        self.add_domain_user_role(
            user=user,
            role=role.id,
            domain='default')

    def get_user(self, user_name):
        """
        It gets the user for its name
        :param user_name: the username
        :return: the user
        """
        users = self.keystone.users.list(username=user_name)
        if users and len(users) == 1:
            return users[0]
        return None

    def create_user(self, user_name, password, role_name, date_now=None):
        """
        It creates a user.
        :param user_name: username
        :param password: password
        :param role_name: the role
        :param date_now: the date to be created
        :return: the user
        """
        users = self.get_user(user_name)
        if users:
            raise Exception(403, "User already exist")

        self.register_user(user_name, password, role_name, date_now)

    def register_user(self, user_name, password, role_name, date_now=None):
        """
        It register the user in the idm.
        :param user_name: username
        :param password: password
        :param role_name: the role
        :param date_now: the date to be created
        :return: the user
        """
        user = self.keystone.user_registration.users.register_user(
                user_name,
                domain="default",
                password=password,
                username=user_name)

        self.keystone.user_registration.users.activate_user(
                user=user.id,
                activation_key=user.activation_key)

        user = self.get_user(user_name)
        if user:
            self.update_domain_to_role(user, role_name, date_now)
            self.update_quota(user, role_name)
        return user

    def update_user(self, user, date=None):
        """
        It updates the users.
        :param user: the user
        :param date: the date
        :return: nothing
        """
        self.update_domain_to_role(user, self.role_name, date)
        self.update_quota(user, self.role_name)

    def delete_user(self, user):
        """
        It deletes the user
        :param user: the user to be deleted.
        :return: nothing
        """
        users = self.keystone.users.list(username=user.username)
        if users or len(users) > 0:
            # We delete the projects belonging to the user
            projects = self.keystone.projects.list(user=users[0])
            for project in projects:
                self.keystone.projects.delete(project)
            self.keystone.users.delete(users[0])
        else:
            raise Exception(404, "User {0} not found".format(user.username))

    def delete_user_id(self, user_id):
        """
        It delete the user by its user_id
        :param user_id: the user_id
        :return: nothing
        """
        users = self.keystone.users.list(username=user_id)
        if users or len(users) > 0:
            self.delete_user(users[0])
        else:
            raise Exception(404, "User {0} not found".format(user_id))

    def delete_trial_users(self):
        """
        It deletes the trial users.
        :return:
        """
        users_trial = self.exp.get_trial_users()
        for user in users_trial:
            self.delete_user(user)

    def delete_community_users(self):
        """
        It deletes the community users.
        :return:
        """
        users_community = self.exp.get_community_users()
        for user in users_community:
            self.delete_user(user)

    def delete_basic_users(self):
        """
        It deletes the basic users.
        :return:
        """
        users_basic = self.exp.get_basic_users()
        for user in users_basic:
            self.delete_user(user)

    def update_quota(self, user, role):
        """ It updates the quota for the user according to role requirements.
        the user should be registrated in keystone.
        :param user: the user
        :param role: the role
        :return: nothing
        """
        kargs = self.get_nova_quota(user, role)
        self.nova_c.quotas.update(user.cloud_project_id, **kargs)
        self.neutron_c.update_quota(user.cloud_project_id, self.get_neutron_quota(role))

    def get_neutron_quota(self, role):
        """
        It gets the neutron quota parameters
        :param role: the user role
        :return: the quota
        """
        if role == 'community':
            return {"quota": {"subnet": 1, "network": 1, "floatingip": 1,
                              "security_group_rule": 20, "security_group": 20,
                              "router": 1, "port": 10}}
        elif role == 'trial':
            return {"quota": {"subnet": 0, "network": 0, "floatingip": 1,
                              "security_group_rule": 10, "security_group": 10,
                              "router": 0, "port": 10}}
        else:
            return {"quota": {"subnet": 0, "network": 0, "floatingip": 0,
                              "security_group_rule": 0, "security_group": 0,
                              "router": 0, "port": 0}}

    def get_nova_quota(self, user, role):
        """
        It gets the nova quota parameters
        :param user: the user
        :param role: the role
        :return: the quota
        """

        if role == 'basic':
            return {"user_id": user.id, "instances": 0, "ram": 0,
                    "cores": 0, "floating_ips": 0}
        elif role == "trial":
            return {"user_id": user.id, "instances": 3, "ram": 6000,
                    "cores": 5, "floating_ips": 1}
        else:
            return {"user_id": user.id, "instances": 5, "ram": 10240,
                    "cores": 10, "floating_ips": 0}
