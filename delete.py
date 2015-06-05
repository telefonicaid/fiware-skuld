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

import time
import base64

import nova
import glance
import cinder
import neutron

import osclients
from change_identity import change_identity

"""Warning: these method destroy all the tenant's resources!!!!!!"""


def delete_tenant_resources():
    nova.delete_user_keypairs()

    # Snapshots must be deleted before the volumes, because a spanpshot depends
    # of a volume. A pause is required.
    cinder.delete_tenant_volume_snapshots()
    nova.delete_tenant_vms()

    # VM must be deleted before purging the security groups
    while cinder.get_tenant_volume_snapshots():
        time.sleep(1)
    nova.delete_tenant_security_groups()

    # TODO: remove rules from default secgroup. It cannot be deleted.

    glance.delete_tenant_images()

    cinder.delete_tenant_volumes()
    cinder.delete_tenant_backup_volumes()

    neutron.delete_tenant_ports()
    neutron.delete_tenant_securitygroups()
    neutron.delete_tenant_floatingips()
    neutron.delete_tenant_subnets()
    neutron.delete_tenant_networks()
    neutron.delete_tenant_routers()

def delete_users_resources(usernames):
    for user in usernames:
        change_identity(user)
        delete_tenant_resources()
        restore_session()
 
# delete_tenant_resources()
