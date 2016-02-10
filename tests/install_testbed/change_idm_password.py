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
__author__ = 'chema'

"""script to change idm user default password with a random one"""

import os.path
from subprocess import check_call

from skuld.change_password import PasswordChanger
from utils.osclients import OpenStackClients

file_path = '/home/ubuntu/idm/conf/settings.py'
etckeystone_path = '/home/ubuntu/idm/keystone/etc/keystone.conf'

credential ="""export OS_AUTH_URL=http://127.0.0.1:5000/v3/
export OS_AUTH_URL_V2=http://127.0.0.1:5000/v2.0/
export OS_USERNAME=idm
export OS_TENANT_NAME=idm
export OS_PROJECT_DOMAIN_ID=default
export OS_USER_DOMAIN_NAME=Default
export OS_REGION_NAME=Spain2
export OS_IDENTITY_API_VERSION=3
"""

# reset the password
osclients = OpenStackClients('http://127.0.0.1:5000/v3/')
osclients.set_credential('idm', 'idm', 'idm')
password_changer = PasswordChanger(osclients)
idm = password_changer.get_user_byname('idm')
new_password = password_changer.reset_password(idm)

# Generate the credential file
with open(os.path.expanduser('~/credential'), 'w') as f:
    f.write(credential)
    f.write('export OS_PASSWORD=' + new_password + '\n')

# Change the password in the settings file
content = open(file_path).read()
content = content.replace("'password': 'idm'", "'password': '" +
                          new_password + "'")
content = content.replace("KEYSTONE_ADMIN_TOKEN = 'ADMIN'",
                          "KEYSTONE_ADMIN_TOKEN = '" + new_password + "'")

with open(file_path, 'w') as f:
    f.write(content)

# Change the admin token in the keystone config file
content = open(etckeystone_path).read()
content = content.replace("admin_token=ADMIN", "admin_token=" + new_password)
with open(etckeystone_path, 'w') as f:
    f.write(content)

# Restart keystone to apply admin_token change
check_call(['sudo', 'service', 'keystone_idm', 'restart'])
