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
import os.path

from fiwareskuld.expired_users import ExpiredUsers
from fiwareskuld.utils import osclients
from fiwareskuld.utils import log
from fiwareskuld.utils import rotated_files
from fiwareskuld.conf import settings

logger = log.init_logs('phase0')


class UsersExpired:
    def __init__(self):
        """Constructor. Create a keystone client"""
        clients = osclients.OpenStackClients()
        clients.override_endpoint(
            'identity', clients.region, 'admin', settings.KEYSTONE_ENDPOINT)
        self.keystoneclient = clients.get_keystoneclientv3()
        self.protected = set()
        self.expiredusers = ExpiredUsers('', '', '')

    def save_community_lists(self, cron_daily=False):
        (notify_list, delete_list) = self.expiredusers.get_yellow_red_community_users()
        self._save_lists(notify_list, delete_list, "community", cron_daily)

    def save_trial_lists(self, cron_daily=False):
        (notify_list, delete_list) = self.expiredusers.get_yellow_red_trial_users()
        self._save_lists(notify_list, delete_list, "trial", cron_daily)

    def _save_lists(self, notify_list, delete_list, start_file, cron_daily=False):
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
        with open("{0}_users_to_notify.txt".format(start_file), 'w') as users_to_notify:
            for user in notify_list:
                users_to_notify.write(user.id + "\n")

        if cron_daily:
            if settings.STOP_BEFORE_DELETE == 0:
                name = "{0}_users_to_delete_phase3.txt".format(start_file)
                with open(name, 'w') as users_to_delete_p3:
                    for user in delete_list:
                        users_to_delete_p3.write(user.id + ',' + user.name + '\n')
            else:
                name = "{0}_users_to_delete.txt".format(start_file)
                phase3_name = "{0}_users_to_delete_phase3.txt".format(start_file)
                basic_users = self.get_basic_users_ids()
                rotated_files.rotate_files(
                    name, settings.STOP_BEFORE_DELETE, phase3_name)
                # Remove from list the users that are not basic
                # (i.e.) users who has changed to community or again to trial
                if os.path.exists(phase3_name):
                    with open(phase3_name, 'r') as phase3:
                        filtered = list(u for u in phase3 if u in basic_users)
                    with open(phase3_name, 'w') as phase3:
                        for user in filtered:
                            phase3.write(user.id + ',' + user.name + '\n')

                with open(name, 'w') as users_to_delete:
                    for user in delete_list:
                        users_to_delete.write(user.id + '\n')

        else:
            with open("{0}_users_to_delete.txt".format(start_file), 'w') as users_to_delete:
                for user in delete_list:
                    users_to_delete.write(user.id + '\n')


if __name__ == '__main__':
    expired = UsersExpired()
    expired.save_community_lists(cron_daily=False)
    expired.save_trial_lists(cron_daily=False)
