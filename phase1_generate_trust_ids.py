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

import logging
import sys
from os import environ as env

from impersonate import TrustFactory
from check_users import CheckUsers
from settings.settings import TRUSTEE
from settings.settings import KEYSTONE_ENDPOINT
from osclients import OpenStackClients
import utils.log


def generate_trust_ids(users_to_delete):
    """
    From a list of users to delete, generate a file with a trustid for each
    user. The user is acting as the trustor, delegating in a trustee, which
    will impersonate it to delete its resources.

    :param users_to_delete: a list of trustors.
    :return: this function does not return anything. It creates a file.
    """
    global logger

    osclients = OpenStackClients()
    users_trusted_ids = open('users_trusted_ids.txt', 'w')

    check_users = CheckUsers()

    # Use an alternative URL that allow direct access to the keystone admin
    # endpoint, because the registered one uses an internal IP address.

    osclients.override_endpoint(
        'identity', osclients.region, 'admin', KEYSTONE_ENDPOINT)

    trust_factory = TrustFactory(osclients)
    lines = users_to_delete.readlines()
    total = len(lines)
    count = 0
    if 'TRUSTEE_USER' in env:
        trustee = env['TRUSTEE_USER']
    else:
        trustee = TRUSTEE

    for user in lines:
        count += 1
        user = user.strip().split(',')[0]
        if user == '':
            continue
        if user not in check_users.users_basic:
            logger.warning('Ignoring user {0} because is not basic'.format(user))
            continue
        try:
            (username, trust_id, user_id) = trust_factory.create_trust_admin(
                user, trustee)
            print >>users_trusted_ids, username + ',' + trust_id + ',' + \
                user_id
            msg = 'Generated trustid for user {0} ({1}) ({2}/{3})'
            logger.info(msg.format(user_id, username, count, total))
        except Exception, e:
            msg = 'Failed getting trust-id from trustor {0}. Reason: {1}'
            logger.error(msg.format(user, str(e)))

    users_trusted_ids.close()


if __name__ == '__main__':
    logger = utils.log.init_logs('phase1')
    if len(sys.argv) == 2:
        name = sys.argv[1]
    else:
        name = 'users_to_delete.txt'

    try:
        users_to_delete = open(name)
    except Exception:
        m = 'Failed reading the file ' + name
        logger.error(m)

    generate_trust_ids(users_to_delete)
else:
    logger = logging.getLogger(__name__)
