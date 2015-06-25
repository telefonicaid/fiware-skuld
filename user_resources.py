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

from osclients import OpenStackClients
from nova_resources import NovaResources
from glance_resources import GlanceResources
from cinder_resources import CinderResources
from neutron_resources import NeutronResources

class UserResources(object):
    """Class to list, delete user resources. Also provides a method to stop all
    the VM of the tenant.

    This class works creating a instance with the credential of the user owner
    of the resources. It does not use an admin credential!!!"""
    def __init__(self, username, password, tenant_id=None, tenant_name=None):
        self.clients = OpenStackClients()
        if tenant_id:
            self.clients.set_credential(username, password, tenant_id, False)
        elif tenant_name:
            self.clients.set_credential(username, password, tenant_name)
        else:
            raise('Either tenant_id or tenant_name must be provided')

        self.nova = NovaResources(self.clients)
        self.cinder = CinderResources(self.clients)
        self.glance = GlanceResources(self.clients)
        self.neutron = NeutronResources(self.clients)

    def delete_tenant_resources(self):
        self.nova.delete_user_keypairs()

        # Snapshots must be deleted before the volumes, because a spanpshot
        # depends of a volume. A pause is required.
        self.cinder.delete_tenant_volume_snapshots()
        while self.cinder.get_tenant_volume_snapshots():
            time.sleep(1)

        # VM must be deleted before purging the security groups
        self.nova.delete_tenant_vms()

        self.nova.delete_tenant_security_groups()

        # TODO: remove rules from default secgroup. It cannot be deleted.

        self.glance.delete_tenant_images()

        self.cinder.delete_tenant_volumes()
        self.cinder.delete_tenant_backup_volumes()

        self.neutron.delete_tenant_ports()
        self.neutron.delete_tenant_securitygroups()
        self.neutron.delete_tenant_floatingips()
        self.neutron.delete_tenant_subnets()
        self.neutron.delete_tenant_networks()
        self.neutron.delete_tenant_routers()

    def stop_tenant_vms(self):
        self.nova.stop_tenant_vms()

    def print_tenant_resources(self):
        print 'Tenant id is: ' + self.clients.get_session().get_project_id()
        print 'User id is: ' + self.clients.get_session().get_user_id()
        print 'User keypairs:'
        print self.nova.get_user_keypairs()
        print 'Tenant VMs:'
        print self.nova.get_tenant_vms()
        print 'Tenant security groups (nova):'
        print self.nova.get_tenant_security_groups()

        print 'Tenant images:'
        print self.glance.get_tenant_images()

        print 'Tenant volume snapshots:'
        print self.cinder.get_tenant_volume_snapshots()

        print 'Tenant volumes:'
        print self.cinder.get_tenant_volumes()

        print 'Tenant backup volumes:'
        print self.cinder.get_tenant_backup_volumes()

        print 'Tenant floating ips:'
        print self.neutron.get_tenant_floatingips()
        print 'Tenant networks:'
        print self.neutron.get_tenant_networks()
        print 'Tenant security groups (neutron):'
        print self.neutron.get_tenant_securitygroups()
        print 'Tenant routers:'
        print self.neutron.get_tenant_routers()
        print 'Tenant subnets'
        print self.neutron.get_tenant_subnets()
        print 'Tenant ports'
        print self.neutron.get_tenant_ports()

