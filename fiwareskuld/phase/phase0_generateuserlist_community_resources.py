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
from fiwareskuld.conf import settings
from fiwareskuld.utils import log
from fiwareskuld.utils import rotated_files
from fiwareskuld.users_management import UserManager
from fiwareskuld.conf import settings

__author__ = 'henar'

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
        users = ExpiredUsers('', '', '')

        community_users = users.get_community_users()

        user_manager = UserManager()

        with open('community_users_regions.txt', 'w') as users_to_delete:
            for user in community_users:
                users_to_delete.write(user.id + " " + user.name + " " + user.community_started_at + " ")
                regions = user_manager.get_regions(user)
                if regions:
                    users_to_delete.write(user_manager.get_regions(user))
                else:
                    users_to_delete.write("Projects is not enabled")
                users_to_delete.write("\n")

    def generate_community_users_resources(self):
        users = ExpiredUsers('', '', '')

        community_users = users.get_community_users()

        self._get_community_resources(community_users, 'community_users_regions_resources.txt')

    def generate_expired_community_users_resources(self):
        users = ExpiredUsers('', '', '')

        community_users = users.get_list_expired_community_users()

        self._get_community_resources(community_users, 'expired_community_users_regions_resources.txt')

    def _get_community_resources(self, users, file):
        user_manager = UserManager()

        with open(file, 'w') as users_to_delete:
            for user in users:
                users_to_delete.write(user.id + " " + user.name + " " + user.community_started_at + " ")
                regions = user_manager.get_regions(user)
                if regions and "PiraeusUHannoverSpain2Karlsk" in regions:
                    users_to_delete.write("Projects is not enabled\n")
                    continue
                resources = user_manager.get_user_resources_regions(user)

                for resource in resources:
                    if type(resources) is dict:
                        if "SophiaAntipolis2" in resource:
                            users_to_delete.write("Region SophiaAntipolis2")
                            continue
                        if resources[resource]:
                            if "vms" in resources[resource]:
                                users_to_delete.write("Region " + resource + " vms: " +
                                                      str(len(resources[resource]["vms"])) + " ")
                            else:
                                users_to_delete.write("Region " + resource + " problems to obtain vms")
                        else:
                            users_to_delete.write("Projects is not enabled")
                users_to_delete.write("\n")

    def save_lists(self, cron_daily=False):
        """Create files users_to_delete.txt and users_to_notify.txt with the
        users expired and users that will expire in a week or less.

        If settings.STOP_BEFORE_DELETE !=0 and cron_daily=True, it also creates
        users_to_delete_phase3.txt (in this case, users_to_delete.txt is for
        the phase2). To create the file users_to_delete_phase3.txt, the files
        users_to_delete.txt are rotated in each daily execution; when the file
        reaches the settings.STOP_BEFORE_DELETE rotation, the file is renamed
        to users_to_delete_phase3.txt.

        if settings.STOP_BEFORE_DELETE ==0 and cron_daily=True, file
        users_to_delete.txt is renamed to users_to_delete_phase3.txt.

        :param cron_daily: this code is invoked from a cron daily script.
          if implies the creation of file users_to_delete_phase3.txt
        :return: nothing
        """
        expiredusers = ExpiredUsers('', '', '')

        delete_list = expiredusers.get_community_users()
        with open('expired_community_users.txt', 'w') as users_to_delete:
            for user in delete_list:
                users_to_delete.write(user.id + " " + user.name + " " + user.community_started_at + "\n ")


if __name__ == '__main__':
    users = CommunityUsers()
    users.generate_community_users_regions()
    users.generate_community_users_resources()
    users.save_lists(cron_daily=False)
