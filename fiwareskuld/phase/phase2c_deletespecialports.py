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
import sys
import logging

from fiwareskuld.special_ports import SpecialPortRemover
from fiwareskuld.utils import log


class SpecialPortsRemover(object):
    """Class to delete ports associated to routers not owned by the port
    owner. To delete these ports, an admin credential is needed"""

    def __init__(self):
        """constructor"""
        self.logger = logging.getLogger(__name__)
        self.special_port = SpecialPortRemover()

    def get_users_from_file(self, file):
        """
        Read the file with the users to delete and returns a list
        :return: a list with the ids of the users to delete
        """
        try:
            users = open(file)
        except Exception:
            self.logger.error('The users_to_delete.txt file must exists')
            sys.exit(-1)

        list_users = list()
        for line in users.readlines():
            user_id = line.strip().split(',')[0]
            if user_id == '':
                continue
            list_users.append(user_id)
        return list_users

    def delete_special_ports_community(self):
        """
        delete the users' ports that are interfaces in routers of a
        different tenant; these ports can not be deleted without an admin
        credential for community users.
        :return: nothing
        """
        users_id = self.get_users_from_file("community_users_to_delete.txt")
        self.special_port.delete_special_ports(users_id)

    def delete_special_ports_trial(self):
        """
        delete the users' ports that are interfaces in routers of a
        different tenant; these ports can not be deleted without an admin
        credential for trial users.
        :return: nothing
        """
        users_id = self.get_users_from_file("trial_users_to_delete.txt")
        self.special_port.delete_special_ports(users_id)

if __name__ == '__main__':
    logger = log.init_logs('phase2c_deletespecialports')
    remover = SpecialPortsRemover()
    remover.delete_special_ports_community()
    remover.delete_special_ports_trial()
