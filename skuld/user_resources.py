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

import time
import logging

import impersonate
from conf import settings
from utils.osclients import OpenStackClients
from skuld.nova_resources import NovaResources
from skuld.glance_resources import GlanceResources
from skuld.cinder_resources import CinderResources
from skuld.neutron_resources import NeutronResources
from skuld.blueprint_resources import BluePrintResources
from swift_resources import SwiftResources


class UserResources(object):
    """Class to list, delete user resources. Also provides a method to stop all
    the VM of the tenant.

    This class works creating a instance with the credential of the user owner
    of the resources. It does not use an admin credential!!!"""
    def __init__(self, username, password, tenant_id=None, tenant_name=None,
                 trust_id=None):
        """
        Constructor of the class. Tenant_id or tenant_name or tust_id must be
        provided.

        There are two ways of using this class:
        -passing the user, password, tenant_id or tenant_name of the user whose
        resources are being deleted
        -passing the user and password of the trustee, and the trust_id
        generated to impersonate the trustor.

        :param username: the user name whose resources are deleted
          or the user name of the trustee
        :param password: the password of the user whose resources are deleted
          or the password of the trustee
        :param tenant_id: the tenant id of the user whose resources must be
        deleted.
        :param tenant_name: the tenant name of the user whose resources must be
         deleted
        :param trust_id: the trust_id used to impersonate the user whose
        resources must be deleted
        :return: nothing
        """

        self.logger = logging.getLogger(__name__)
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
        region = self.clients.region
        self.clients.override_endpoint(
            'identity', region, 'admin', settings.KEYSTONE_ENDPOINT)
        self.user_id = self.clients.get_session().get_user_id()
        session = self.clients.get_session()
        self.user_name = username
        self.nova = NovaResources(self.clients)
        self.cinder = CinderResources(self.clients)
        self.glance = GlanceResources(self.clients)
        try:
            self.neutron = NeutronResources(self.clients)
        except Exception:
            # The region does not support Neutron
            # It would be better to check the endpoint
            self.neutron = None
        self.blueprints = BluePrintResources(self.clients)
        try:
            self.swift = SwiftResources(self.clients)
        except Exception:
            # The region does not support Swift
            # It would be better to check the endpoint
            self.swift = None
        # Images in use is a set used to avoid deleting formerly glance images

        # in use by other tenants
        self.imagesinuse = set()

        # Regions the user has access
        self.regions_available = set()
        self.regions_available.update(self.clients.get_regions('compute'))

    def change_region(self, region):
        """
        change the region. All the clients need to be updated, but the
        session does not.
        :param region: the name of the region
        :return: nothing.
        """
        self.clients.set_region(region)
        self.clients.override_endpoint(
            'identity', region, 'admin', settings.KEYSTONE_ENDPOINT)
        self.nova.on_region_changed()
        self.glance.on_region_changed()
        try:
            if self.swift:
                self.swift.on_region_changed()
            else:
                self.swift = SwiftResources(self.clients)
        except Exception:
            # The region does not support swift
            self.swift = None

        self.cinder.on_region_changed()
        self.blueprint.on_region_changed()
        try:
            if self.neutron:
                self.neutron.on_region_changed()
            else:
                self.neutron = NeutronResources(self.clients)
        except Exception:
            # The region does not support neutron
            self.neutron = None

    def delete_tenant_resources_pri_1(self):
        """Delete here all the elements that do not depend of others are
        deleted first"""

        try:
            self.nova.delete_user_keypairs()
        except Exception, e:
            msg = 'Deletion of keypairs failed. Reason: '
            self.logger.error(msg + str(e))

        # Snapshots must be deleted before the volumes, because a snapshot
        # depends of a volume.
        try:
            self.cinder.delete_tenant_volume_snapshots()
        except Exception, e:
            msg = 'Deletion of volume snaphosts failed. Reason: '
            self.logger.error(msg + str(e))

        # Blueprint instances must be deleted before VMs, instances before
        # templates
        try:
            self.blueprints.delete_tenant_blueprints()
        except Exception, e:
            msg = 'Deletion of blueprints failed. Reason: '
            self.logger.error(msg + str(e))

        try:
            self.cinder.delete_tenant_backup_volumes()
        except Exception, e:
            msg = 'Deletion of backup volumes failed. Reason: '
            self.logger.error(msg + str(e))

        try:
            if self.swift:
                self.swift.delete_tenant_containers()
        except Exception, e:
            msg = 'Deletion of swift containers failed. Reason'
            self.logger.error(msg + str(e))

    def delete_tenant_resources_pri_2(self):
        """Delete resources that must be deleted after p1 resources"""
        # VMs and blueprint templates should be deleted after blueprint
        # instances.

        count = 0
        while self.blueprints.get_tenant_blueprints() and count < 120:
            time.sleep(1)
            count += 1
        if count >= 120:
            self.logger.warning('Waiting for blueprint more than 120 seconds')
        try:
            self.nova.delete_tenant_vms()
        except Exception, e:
            msg = 'Deletion of VMs failed. Reason: '
            self.logger.error(msg + str(e))

        # Blueprint instances must be deleted after blueprint templates
        try:
            self.blueprints.delete_tenant_templates()
        except Exception, e:
            msg = 'Deletion of blueprint templates failed. Reason: '
            self.logger.error(msg + str(e))

    def delete_tenant_resources_pri_3(self):
        """Delete resources that must be deleted after p2 resources"""
        count = 0
        while self.nova.get_tenant_vms() and count < 120:
            time.sleep(1)
            count += 1
        if count >= 120:
            self.logger.warning('Waiting for VMs more than 120 seconds')

        # security group, volumes, network ports, images, floating ips,
        # must be deleted after VMs

        # self.glance.delete_tenant_images()
        try:
            self.glance.delete_tenant_images_notinuse(self.imagesinuse)
        except Exception, e:
            msg = 'Deletion of images failed. Reason: '
            self.logger.error(msg + str(e))

        # Before deleting volumes, snapshot volumes must be deleted
        count = 0
        while self.cinder.get_tenant_volume_snapshots() and count < 120:
            time.sleep(1)
            count += 1
        if count >= 120:
            self.logger.warning('Waiting for volume snapshots > 120 seconds')

        try:
            self.cinder.delete_tenant_volumes()
        except Exception, e:
            msg = 'Deletion of volumes failed. Reason: '
            self.logger.error(msg + str(e))

        try:
            self.neutron.delete_tenant_ports()
        except Exception, e:
            msg = 'Deletion of network ports failed. Reason: '
            self.logger.error(msg + str(e))

        try:
            self.neutron.delete_tenant_securitygroups()
        except Exception, e:
            msg = 'Deletion of network security groups failed. Reason: '
            self.logger.error(msg + str(e))

        try:
            self.nova.delete_tenant_security_groups()
        except Exception, e:
            msg = 'Deletion of security groups failed. Reason: '
            self.logger.error(msg + str(e))

        try:
            self.neutron.delete_tenant_floatingips()
        except Exception, e:
            msg = 'Deletion of floating ips failed. Reason: '
            self.logger.error(msg + str(e))

        try:
            self.neutron.delete_tenant_subnets()
        except Exception, e:
            msg = 'Deletion of subnets failed. Reason: '
            self.logger.error(msg + str(e))

        try:
            self.neutron.delete_tenant_networks()
        except Exception, e:
            msg = 'Deletion of networks failed. Reason: '
            self.logger.error(msg + str(e))

        try:
            self.neutron.delete_tenant_routers()
        except Exception, e:
            msg = 'Deletion of routers failed. Reason: '
            self.logger.error(msg + str(e))

    def delete_tenant_resources(self):
        """Delete all the resources of the tenant, and also the keypairs of the
        user"""
        self.delete_tenant_resources_pri_1()
        time.sleep(10)
        self.delete_tenant_resources_pri_2()
        self.delete_tenant_resources_pri_3()

    def stop_tenant_vms(self):
        """Stop all the active vms of the tenant
        :return:  stopped vms
        """
        return self.nova.stop_tenant_vms()

    def unshare_images(self):
        """Make private all the tenant public images"""
        if self.glance:
            self.glance.unshare_images()

    def get_resources_dict(self):
        """return a dictionary of sets with the ids of the user's resources
        :return: a dictionary with the user's resources
        """
        resources = dict()
        resources['blueprints'] = set(self.blueprints.get_tenant_blueprints())
        resources['templates'] = set(self.blueprints.get_tenant_templates())
        resources['keys'] = set(self.nova.get_user_keypairs())
        resources['vms'] = set(self.nova.get_tenant_vms())
        resources['security_groups'] = set(
            self.nova.get_tenant_security_groups())
        resources['images'] = self.glance.get_tenant_images()
        resources['volumesnapshots'] = set(
            self.cinder.get_tenant_volume_snapshots())
        resources['volumes'] = set(self.cinder.get_tenant_volumes())
        resources['backupvolumes'] = set(
            self.cinder.get_tenant_backup_volumes())
        if self.neutron:
            resources['floatingips'] = set(
                self.neutron.get_tenant_floatingips())
            resources['networks'] = set(
                self.neutron.get_tenant_networks())
            resources['nsecuritygroups'] = set(
                self.neutron.get_tenant_securitygroups())
            resources['routers'] = set(self.neutron.get_tenant_routers())
            resources['subnets'] = set(self.neutron.get_tenant_subnets())
            resources['ports'] = set(self.neutron.get_tenant_ports())
        if self.swift:
            resources['objects'] = set(self.swift.get_tenant_objects())

        return resources

    def print_tenant_resources(self):
        """print all the tenant's resources"""
        print('Tenant id is: ' + self.clients.get_session().get_project_id())
        print('User id is: ' + self.clients.get_session().get_user_id())

        print('Tenant blueprint instances: ')
        print(self.blueprints.get_tenant_blueprints())
        print('Tenant blueprint templates: ')
        print(self.blueprints.get_tenant_templates())

        print('User keypairs:')
        print(self.nova.get_user_keypairs())
        print('Tenant VMs:')
        print(self.nova.get_tenant_vms())
        print('Tenant security groups (nova):')
        print(self.nova.get_tenant_security_groups())

        print('Tenant images:')
        print(self.glance.get_tenant_images())

        print('Tenant volume snapshots:')
        print(self.cinder.get_tenant_volume_snapshots())
        print('Tenant volumes:')
        print(self.cinder.get_tenant_volumes())
        print('Tenant backup volumes:')
        print(self.cinder.get_tenant_backup_volumes())

        if self.neutron:
            print('Tenant floating ips:')
            print(self.neutron.get_tenant_floatingips())
            print('Tenant networks:')
            print(self.neutron.get_tenant_networks())
            print('Tenant security groups (neutron):')
            print(self.neutron.get_tenant_securitygroups())
            print('Tenant routers:')
            print(self.neutron.get_tenant_routers())
            print('Tenant subnets')
            print(self.neutron.get_tenant_subnets())
            print('Tenant ports')
            print(self.neutron.get_tenant_ports())

        if self.swift:
            print('Containers')
            print(self.swift.get_tenant_containers())

    def free_trust_id(self):
        """Free trust_id, if it exists.

        :return: nothing
        """
        if self.trust_id:
            self.logger.info('Freeing trust-id of user ' + self.user_id)
            trust = impersonate.TrustFactory(self.clients)
            trust.delete_trust(self.trust_id)
