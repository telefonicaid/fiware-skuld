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


    def add_domain_user_role(self, user, role, domain):
        """ It adds a role to a user.
        :param user: the user
        :param role: the role to add
        :param domain: the domain
        :return:
        """
        manager = self.keystone.roles
        return manager.grant(role, user=user, domain=domain)

    def update_domain_to_role(self, user, role_name, date_now=None, duration=100):
        """
        It updates the domain to the role
        :param user: the user
        :param role_name: the role
        :param duration: the duration for community
        :return:
        """
        role = self.keystone.roles.find(name=role_name)

        if date_now:
            date_out = str(date_now)
        else:
            date_out = str(datetime.date.today())

        if self.role_name == "community":
            self.keystone.users.update(user, community_started_at=date_out, community_duration=duration)

        if self.role_name == "trial":
            self.keystone.users.update(user, trial_started_at=date_out)

        self.add_domain_user_role(
            user=user,
            role=role.id,
            domain='default')

    def create_user(self, user_name, password, role_name, date_now=None):
        """ It creates a user
        :return:
        """
        self.user_name = user_name
        self.password = password
        self.tenant_name = user_name
        self.role_name = role_name
        users = self.keystone.users.list(username=self.user_name)
        if len(users) > 0:
            raise Exception(403, "User already exist")
        user = self.keystone.user_registration.users.register_user(
                self.user_name,
                domain="default",
                password=self.password,
                username=self.user_name)

        self.keystone.user_registration.users.activate_user(
                user=user.id,
                activation_key=user.activation_key)
        users = self.keystone.users.list(username=self.user_name)

        self.update_domain_to_role(users[0], self.role_name, date_now)
        self.update_quota(users[0], self.role_name)
        return users[0]

    def update_user(self, user, date=None):
        self.update_domain_to_role(user, self.role_name, date)
        self.update_quota(user, self.role_name)

    def delete_user(self, user):
        """ It creates a user
        :return:
        """
        d = self.keystone.users.list(username = user.username)
        if d or len(d) > 0:
            projects = self.keystone.projects.list(user=d[0])
            for pro in projects:
                self.keystone.projects.delete(pro)
            self.keystone.users.delete(d[0])

    def delete_user_id(self, user_id):
        print "Deleting" + user_id
        d = self.keystone.users.list(username = user_id)
        self.delete_user(d[0])


    def update_quota(self, user, role):
        """ It updates the quota for the user according to role requirements
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
        :return:
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
        It gest the nova quota parameters
        :param user: the user
        :param role: the role
        :return: nothing
        """

        if role == 'basic':
            return {"user_id": user.id, "instances": 0, "ram": 0,
                    "cores": 0, "floating_ips": 0}
        elif role == "trial":
            return {"user_id": user.id, "instances": 3, "ram": 0,
                    "cores": 0, "floating_ips": 1}
        else:
            return {"user_id": user.id, "instances": 5, "ram": 10240,
                    "cores": 10, "floating_ips": 0}
