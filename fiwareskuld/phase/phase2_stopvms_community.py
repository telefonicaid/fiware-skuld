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
import cPickle as pickle
import datetime
from fiwareskuld.utils import log
from fiwareskuld.users_management import UserManager
import os


logger = log.init_logs('phase2')

dict_vms = dict()
failed_users = set()

if os.path.exists('community_users_to_delete.txt'):
    users_to_delete = open('community_users_to_delete.txt')
    lines = users_to_delete.readlines()
    user_count = 0
    user_total = len(lines)
    user_manager = UserManager()
    for user_id in lines:
        try:
            vms = user_manager.stop_vms_in_regions(user_id)
            dict_vms[user_id] = vms
        except Exception, e:
            logger.error('Failed operations with user ' + user_id + ' cause: ' +
                         str(e))
            failed_users.add(user_id)


now = datetime.datetime.now().isoformat()
with open('stopresources_report_' + now + '.pickle', 'wf') as f:
    pickle.dump(dict_vms, f, protocol=-1)

with open('stopresources_error_report_' + now + '.log', 'w') as f:
    for user in failed_users:
        f.write(user + '\n')
