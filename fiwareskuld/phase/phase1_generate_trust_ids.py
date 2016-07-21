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
import logging
import sys

from os import environ as env
from fiwareskuld.impersonate import TrustFactory
from fiwareskuld.conf.settings import TRUSTEE, KEYSTONE_ENDPOINT
from fiwareskuld.utils.osclients import OpenStackClients
from fiwareskuld.check_users import CheckUsers
from fiwareskuld.utils import log


__author__ = 'chema'


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
    check_users.get_ids()

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
        user = user.strip()
        if user == '':
            continue
        try:
            count += 1
            (username, trust_id, user_id) = trust_factory.create_trust_admin(
                user, trustee)
            users_trusted_ids.write(username + ',' + trust_id + ',' + user_id+'\n')
            msg = 'Generated trustid for user {0} ({1}/{2})'
            logger.info(msg.format(user, count, total))
        except Exception, e:
            msg = 'Failed getting trust-id from trustor {0}. Reason: {1}'
            logger.error(msg.format(user, str(e)))

    users_trusted_ids.close()


if __name__ == '__main__':
    OS_AUTH_URL = 'http://130.206.120.23:5000/v2.0'
    OS_USERNAME = 'idm'
    OS_PASSWORD = 'idm'
    OS_TENANT_NAME = 'idm'
    OS_TENANT_ID = "e76a0d73b1c845a788b118fee6c622a3"
    OS_REGION_NAME = 'Valladolid'
    OS_TRUST_ID = ''

    from os import environ
    environ.setdefault('OS_AUTH_URL', OS_AUTH_URL)
    environ.setdefault('OS_USERNAME', OS_USERNAME)
    environ.setdefault('OS_PASSWORD', OS_PASSWORD)
    environ.setdefault('OS_TENANT_NAME', OS_TENANT_NAME)
    environ.setdefault('OS_TENANT_ID', OS_TENANT_ID)
    environ.setdefault('OS_REGION_NAME', OS_REGION_NAME)
    logger = log.init_logs('phase1')
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
