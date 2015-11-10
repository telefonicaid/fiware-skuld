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

import queries
import requests
import logging
import warnings
import utils.log
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from requests.packages.urllib3.exceptions import InsecurePlatformWarning

import settings.settings

logger = utils.log.init_logs('phase0c')

trial = settings.settings.TRIAL_ROLE_ID
basic = settings.settings.BASIC_ROLE_ID
q = queries.Queries()
keystone = q.osclients.get_keystoneclientv3()
warnings.simplefilter('ignore', category=InsecureRequestWarning)
warnings.simplefilter('ignore', category=InsecurePlatformWarning)

def change_user_keystone(user_id):
    """Change the user from trial to basic
    We use this on our testing environment
    :param user_id:
    :return: nothing
    """
    path = '/domains/default/users/{0}/roles/{1}'
    if q.get_type_fiware_user(user_id) != 'trial':
        logging.error('{0} is not a trial user'.format(user_id))
        return

    keystone.role_assignments.client.put(path.format(user_id, basic))
    keystone.role_assignments.client.delete(path.format(user_id, trial))


def change_user_via_idm(user_id):
    """Change the user from trial to basic
    This method must be used in production.
    :param user_id:
    :return: nothing
    """
    if q.get_type_fiware_user(user_id) != 'trial':
        logger.error('{0} is not a trial user'.format(user_id))
    body = {'user_id': user_id, 'role_id': basic, 'notify': True}
    headers = {'X-Auth-Token': q.osclients.get_token()}

    # NOTE(garcianavalon) sometimes in settings people use the end /
    horizon_url = settings.settings.HORIZON_ENDPOINT
    if horizon_url.endswith('/'):
        horizon_url = horizon_url[:-1]

    r = requests.post(horizon_url + '/account_category',
                      json=body, headers=headers, verify=False)
    if r.status_code not in (200, 204):
        msg = 'The operation returned code {0}: {1}'
        logger.error(msg.format(r.status_code, r.reason))
        raise Exception('Server error')

if __name__ == '__main__':
    users = open('users_to_delete.txt')
    for line in users.readlines():
        user_id = line.strip().split(',')[0]
        if user_id == '':
            continue
        logger.info('Changing user {0} from trial to basic'.format(user_id))
        try:
            change_user_via_idm(user_id)
        except Exception, e:
            logger.error('Error changing user {0} to basic. Cause: {1}'.format(
                user_id, str(e)))
