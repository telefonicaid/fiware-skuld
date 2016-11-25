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
from datetime import datetime
import os.path

from fiwareskuld.expired_users import ExpiredUsers
from fiwareskuld.utils import osclients
from fiwareskuld.utils import log
from fiwareskuld.users_management import UserManager
from fiwareskuld.conf import settings

logger = log.init_logs('phase0')


class CommunityUsers:
    def __init__(self):
        """Constructor. Create a keystone client"""
        clients = osclients.OpenStackClients()
        clients.override_endpoint(
            'identity', clients.region, 'admin', settings.KEYSTONE_ENDPOINT)
        self.keystoneclient = clients.get_keystoneclientv3()
        self.protected = set()

    def generate_community_users_regions(self):
        """
        It generates a file with the community users and the regions
        where they have access.
        :return: nothing
        """
        users = ExpiredUsers('', '', '')

        community_users = users.get_community_users()

        self._get_regions_users(community_users, "community_users_regions.txt")

    def generate_expired_community_users_regions(self):
        """
        It generates a file with the expired community users and the regions
        where they have access.
        :return: nothing
        """
        users = ExpiredUsers('', '', '')

        community_users = users.get_list_expired_community_users()

        self._get_regions_users(community_users, "expired_community_users_regions.txt")

    def generate_community_users_resources(self):
        """
        It generates a file with the community expired users.
        :return: nothing
        """
        users = ExpiredUsers('', '', '')

        community_users = users.get_community_users()

        self._get_community_resources(community_users, 'community_users_regions_resources.txt')

    def generate_expired_community_users_resources(self):
        """
        It generates a file with the community expired users resources.
        :return: nothing
        """
        users = ExpiredUsers('', '', '')

        community_users = users.get_list_expired_community_users()

        self._get_community_resources(community_users, 'expired_community_users_regions_resources.txt')

    def _get_community_resources(self, users, file):
        user_manager = UserManager()

        with open(file, 'w') as users_to_delete:
            for user in users:
                users_to_delete.write(user.id + "," + user.name + "," + user.community_started_at + ",")
                regions = user_manager.get_regions(user)
                if regions and "PiraeusU;Hannover;Spain2;Karlsk" in regions:
                    users_to_delete.write("All regions\n")
                    continue
                resources = user_manager.get_user_resources_regions(user)

                for resource in resources:
                    if type(resources) is dict:
                        if resources[resource]:
                            if "vms" in resources[resource]:
                                users_to_delete.write("Region " + resource + " vms: " +
                                                      str(len(resources[resource]["vms"])) + " ")
                            else:
                                users_to_delete.write("Region " + resource + " problems to obtain vms")
                        else:
                            users_to_delete.write("Projects is not enabled")
                users_to_delete.write("\n")

    def _get_regions_users(self, community_users, file):
        user_manager = UserManager()

        with open(file, 'w') as users_to_delete:
            for user in community_users:
                users_to_delete.write(user.id + "," + user.name + "," + user.community_started_at + ",")
                regions = user_manager.get_regions(user)
                if regions:
                    users_to_delete.write(regions)
                else:
                    users_to_delete.write("Projects is not enabled")
                users_to_delete.write("\n")

if __name__ == '__main__':
    users = CommunityUsers()
    users.generate_community_users_regions()
    users.generate_expired_community_users_regions()
    users.generate_community_users_resources()
    users.generate_expired_community_users_resources()
