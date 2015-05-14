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

import nova
import glance
import cinder
import neutron

"""Warning: this methods destroy all the resources of the tenant!!!!!!"""
def delete_tenant_resources():
    nova.delete_user_keypairs()
    nova.delete_tenant_vms()

    # VM must be deleted before purging the security groups
    time.sleep(3)
    nova.delete_tenant_security_groups()
    # TODO: remove rules from default secgroup. This secgroup cannot be deleted.

    glance.delete_tenant_images()

    # Snapshots must be deleted before the volumes, because a spanpshot depends
    # of a volume.
    cinder.delete_tenant_volume_snapshots()
    cinder.delete_tenant_volumes()
    cinder.delete_tenant_backup_volumes()

    #neutron.delete_tenant_subnets()
    neutron.delete_tenant_ports()
    neutron.delete_tenant_floatingips()
    neutron.delete_tenant_networks()
    neutron.delete_tenant_routers()
    neutron.delete_tenant_securitygroups()


# delete_tenant_resources()