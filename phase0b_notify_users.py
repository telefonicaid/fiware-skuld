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
author = 'chema'

import requests
import logging
import warnings
from requests.packages.urllib3.exceptions import InsecureRequestWarning

from osclients import osclients
import settings.settings

def notify_users(user_ids):
    """
    Notify users about the deletion of their resources sending an email to
    each one.
    :param user_ids: the list of user ids
    :return: nothing
    """
    body = {'users': user_ids}
    headers = {'X-Auth-Token': osclients.get_token()}

    horizon_url = settings.settings.HORIZON_ENDPOINT
    if horizon_url.endswith('/'):
        horizon_url = horizon_url[:-1]

    r = requests.post(horizon_url + '/notify_expire_users',
                      json=body, headers=headers, verify=False)
    if r.status_code not in (200, 204):
        msg = 'The operation returned code {0}: {1}'
        logging.error(msg.format(r.status_code, r.reason))

warnings.simplefilter('ignore', category=InsecureRequestWarning)
users = open('users_to_delete.txt')
list_users = list()
for line in users.readlines():
    user_id = line.strip()

    if user_id == '':
        continue
    list_users.append(user_id)

if list_users:
    logging.info('Notifying {0} users'.format(len(list_users)))
    notify_users(list_users)
