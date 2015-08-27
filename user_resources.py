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
import logging

import impersonate
from osclients import OpenStackClients
from nova_resources import NovaResources
from glance_resources import GlanceResources
from cinder_resources import CinderResources
from neutron_resources import NeutronResources
from blueprint_resources import BluePrintResources


class UserResources(object):
    """Class to list, delete user resources. Also provides a method to stop all
    the VM of the tenant.

    This class works creating a instance with the credential of the user owner
    of the resources. It does not use an admin credential!!!"""
    def __init__(self, username, password, tenant_id=None, tenant_name=None,
                 trust_id=None):
        self.clients = OpenStackClients()
        if tenant_id:
            self.clients.set_credential(username, password,
                                        tenant_id=tenant_id)
        elif tenant_name:
            self.clients.set_credential(username, password,
                                        tenant_name=tenant_name)
        elif trust_id:
            self.clients.set_credential(username, password, trust_id=trust_id)
            self.trust_id = trust_id
        else:
            raise(
                'Either tenant_id or tenant_name or trust_id must be provided')

        self.nova = NovaResources(self.clients)
        self.cinder = CinderResources(self.clients)
        self.glance = GlanceResources(self.clients)
        self.neutron = NeutronResources(self.clients)
        self.blueprints = BluePrintResources(self.clients)
        # Images in use is a set used to avoid deleting formerly glance images
        # in use by other tenants
        self.imagesinuse = set()

    def delete_tenant_resources(self):
        """Delete all the resources of the tenant, and also the keypairs of the
        user"""

        self.nova.delete_user_keypairs()

        # Snapshots must be deleted before the volumes, because a snapshot
        # depends of a volume. A pause is required.
        self.cinder.delete_tenant_volume_snapshots()
        while self.cinder.get_tenant_volume_snapshots():
            time.sleep(1)

        # Blueprint instances must be deleted before VMs
        self.blueprints.delete_tenant_blueprints()
        self.blueprints.delete_tenant_templates()

        # VM must be deleted before purging the security groups
        self.nova.delete_tenant_vms()

        self.nova.delete_tenant_security_groups()

        # self.glance.delete_tenant_images()
        self.glance.delete_tenant_images_notinuse(self.imagesinuse)
        self.cinder.delete_tenant_volumes()
        self.cinder.delete_tenant_backup_volumes()

        self.neutron.delete_tenant_ports()
        self.neutron.delete_tenant_securitygroups()
        self.neutron.delete_tenant_floatingips()
        self.neutron.delete_tenant_subnets()
        self.neutron.delete_tenant_networks()
        self.neutron.delete_tenant_routers()

    def stop_tenant_vms(self):
        """Stop all the active vms of the tenant"""
        self.nova.stop_tenant_vms()

    def unshare_images(self):
        """Make private all the tenant public images"""
        self.glance.unshare_images()

    def print_tenant_resources(self):
        """print all the tenant's resources"""
        print 'Tenant id is: ' + self.clients.get_session().get_project_id()
        print 'User id is: ' + self.clients.get_session().get_user_id()

        print 'Tenant blueprint instances: '
        print self.blueprints.get_tenant_blueprints()
        print 'Tenant blueprint templates: '
        print self.blueprints.get_tenant_templates()

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

    def free_trust_id(self):
        """Free trust_id, if it exists.

        :return: nothing
        """
        if self.trust_id:
            logging.info('Freeing trust-id')
            trust = impersonate.TrustFactory(self.clients)
            trust.delete_trust(self.trust_id)

