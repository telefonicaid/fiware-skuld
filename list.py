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

import nova
import glance
import cinder
import neutron
import osclients

tenant_id = osclients.get_session().get_project_id()
print 'Tenant id is: ' + tenant_id
print 'User id is: ' + osclients.get_session().get_user_id()
print 'User keypairs:'
print nova.get_user_keypairs()
print 'Tenant VMs:'
print nova.get_tenant_vms()
print 'Tenant security groups (nova):'
print nova.get_tenant_security_groups()

print 'Tenant images:'
print glance.get_tenant_images()

print 'Tenant volume snapshots:'
print cinder.get_tenant_volume_snapshots()

print 'Tenant volumes:'
print cinder.get_tenant_volumes()

print 'Tenant backup volumes:'
print cinder.get_tenant_backup_volumes()

print 'Tenant floating ips:'
print neutron.get_tenant_floatingips()
print 'Tenant networks:'
print neutron.get_tenant_networks()
print 'Tenant security groups (neutron):'
print neutron.get_tenant_securitygroups()
print 'Tenant routers:'
print neutron.get_tenant_routers()
print 'Tenant subnets'
print neutron.get_tenant_subnets()
print 'Tenant ports'
print neutron.get_tenant_ports()
