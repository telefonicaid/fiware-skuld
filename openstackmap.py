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

from osclients import osclients, OpenStackClients

import cPickle as pickle
import os
import time
from os import environ as env

class OpenStackMap():
    """
    This class build a map from the resources (VMs, networks, images,
    volumes, users, tenants, roles...) in an OpenStack infrastructure.

    This map is optionally cached on disk and can be accessed offline or can be
    used as a metadata snapshot of an OpenStack infrastructure (e.g. to
    analyse resource use and build statistics)
    """

    # objects strategy see the __init__ method documentation
    DIRECT_OBJECTS, NO_CACHE_OBJECTS, REFRESH_OBJECTS, USE_CACHE_OBJECTS = \
        range(4)

    # If use_wrapper is True, dictionaries are wrapped to allow access to
    # resource['field'] also as resource.field. This is not used when
    # objects_strategy is DIRECT_OBJECTS
    use_wrapper = True

    def __init__(
            self, persistence_dir='~/openstackmap', region=None, auth_url=None,
            objects_strategy=USE_CACHE_OBJECTS):
        """
        Constructor
        :param persistence_dir: The path where the data is saved. Ignored if
           objects_strategy is DIRECT_OBJECTS or NO_CACHE_OBJECTS
        :param region: the initial region (if undefined, use OS_REGION_NAME)
        :param auth_url: the keystone URI
        :param objects_strategy: sets the strategy about the object maps
            contained here. It can be:
         * DIRECT_OBJECTS is using the objects as they are got from
           the API. Be careful because methods as delete are available! The
           objects are not cached.
         * NO_CACHE_OBJECTS is using the objects converted to dictionaries, so
           methods to do operations are not available. The objects are not
           cached.
         * REFRESH_OBJECTS is using the objects converted to dictionaries. The
           objects are cached: the new version replace the old one.
         * USE_CACHE_OBJECTS is using the objects converted to dictionaries. If
           a cached copy of the objects are available, it is used.

         Note that neutron objects returned by the API are already dictionaries
        """

        if auth_url:
            self.osclients = OpenStackClients(auth_url=auth_url)
        else:
            self.osclients = OpenStackClients()

        if 'KEYSTONE_ADMIN_ENDPOINT' in os.environ:
            self.osclients.override_endpoint(
                'identity', self.osclients.region, 'admin',
                os.environ['KEYSTONE_ADMIN_ENDPOINT'])

        if region:
            self.osclients.set_region(region)
        else:
            if 'OS_REGION_NAME' not in env:
                raise Exception('Region parameter must be provided or '
                                'OS_REGION_NAME variable must be defined.')
            else:
                region = env['OS_REGION_NAME']

        self.objects_strategy = objects_strategy

        self.persistence_dir = os.path.expanduser(persistence_dir)
        self.pers_region = self.persistence_dir + '/' + region
        self.pers_keystone = self.persistence_dir + '/keystone'

        if objects_strategy not in (OpenStackMap.DIRECT_OBJECTS,
                                    OpenStackMap.NO_CACHE_OBJECTS):
            if not os.path.exists(self.persistence_dir):
                os.mkdir(self.persistence_dir)

            if not os.path.exists(self.pers_keystone):
                os.mkdir(self.pers_keystone)

            if not os.path.exists(self.pers_region):
                os.mkdir(self.pers_region)

        self._init_resource_maps()

    def _init_resource_maps(self):
        """init all the resources that will be available
        as empty dictionaries"""
        # Keystone resources
        self.users = dict()
        self.users_by_name = dict()
        self.roles = dict()
        self.tenants = dict()
        self.tenants_by_name = dict()
        self.roles_a = list()
        self.roles_by_project = dict()
        self.roles_by_user = dict()
        # Glance resources
        self.images = dict()
        # Neutron resources
        self.networks = dict()
        self.subnets = dict()
        self.routers = dict()
        self.floatingips = dict()
        self.ports = dict()
        self.security_groups = dict()
        # Nova resources
        self.vms = dict()
        self.flavors = dict()
        # Cinder resources
        self.volumes = dict()
        self.volume_backups = dict()
        self.volume_snapshots = dict()

    def _load(self, name):
        """Load the resources persisted with pickle. This resources (e.g.
        networks, vms, images...) are saved independently for each region.

        This method is called for load_cinder, load_nova, load_glance,
        load_neutron...

        :param name: the resource name
        :return: a dictionary of objects (dictionaries) indexed by id
        """
        objects = pickle.load(open(self.pers_region + '/' + name +
                                   '.pickle', 'rb'))
        return self._convert(objects)

    def _load_fkeystone(self, name):
        """Load the keystone objects persisted with pickle. This resources are
        shared among the regions. This method is used in load_keystone

        :param name: the resource name
        :return: a list/dictionary of objects (dictionaries)
        """
        objects = pickle.load(open(self.pers_keystone + '/' + name +
                                   '.pickle', 'rb'))
        return self._convert(objects)

    def _convert(self, objects):
        """if use_wrapper, convert objects from dictionary to __E class;
        this class allows accessing  a['key'] also as a.key"""
        if self.use_wrapper and len(objects) > 0:
            class __E(dict):
                def __init__(self, d=dict()):
                    self.__dict__ = self
                    dict.__init__(self, d)

            if isinstance(objects, dict):
                if not isinstance(objects.values()[0], dict):
                    return objects
                return dict((key, __E(objects[key])) for key in objects)
                return objects
            else:
                return list(__E(object) for object in objects)

        else:
            return objects

    def _get_keystone_data(self):
        """get data from keystone server"""
        dict_object = self.objects_strategy != OpenStackMap.DIRECT_OBJECTS
        save = dict_object and \
            self.objects_strategy != OpenStackMap.NO_CACHE_OBJECTS
        keystone = self.osclients.get_keystoneclientv3()
        roles = keystone.roles.list()
        users = keystone.users.list()
        tenants = keystone.projects.list()
        roles_a = keystone.role_assignments.list()

        roles_by_user = dict()
        roles_by_project = dict()

        for roleasig in roles_a:
            try:
                userid = roleasig.user['id']
                if 'project' in roleasig.scope:
                    projectid = roleasig.scope['project']['id']
                else:
                    projectid = str(roleasig.scope)
                roleid = roleasig.role['id']
                if userid not in roles_by_user:
                    roles_by_user[userid] = list()
            except AttributeError:
                # Discard roles not assigned to users
                continue

            if projectid not in roles_by_project:
                roles_by_project[projectid] = list()
            roles_by_user[userid].append((roleid, projectid))
            roles_by_project[projectid].append((roleid, userid))

        self.roles_by_user = roles_by_user
        self.roles_by_project = roles_by_project

        tenants_by_name = dict()
        users_by_name = dict()
 
        if dict_object:
            roles = dict((role.id, role.to_dict()) for role in roles)
            users = dict((user.id, user.to_dict()) for user in users)
            tenants = dict((tenant.id, tenant.to_dict()) for tenant in tenants)
            roles_a = list(asig.to_dict() for asig in roles_a)
            for tenant in tenants.values():
                tenants_by_name[tenant['name']] = tenant
            tenants_by_name = dict()
            for user in users.values():
                users_by_name[user['name']] = user
        else:
            self.roles = dict((role.id, role) for role in roles)
            self.users = dict((user.id, user) for user in users)
            self.tenants = dict((tenant.id, tenant) for tenant in tenants)
            self.roles_a = roles_a

            tenants_by_name = dict()
            for tenant in tenants:
                if getattr(tenant, 'name', None):
                    tenants_by_name[tenant.name] = tenant

            for user in users:
                if getattr(user, 'name', None):
                    users_by_name[user.name] = user

            self.tenants_by_name = tenants_by_name
            self.users_by_name = users_by_name
            return

        if save:
            with open(self.pers_keystone + '/roles.pickle', 'wb') as f:
                pickle.dump(roles, f, protocol=-1)

            with open(self.pers_keystone + '/users.pickle', 'wb') as f:
                pickle.dump(users, f, protocol=-1)

            with open(self.pers_keystone + '/users_by_name.pickle', 'wb') as f:
                pickle.dump(users_by_name, f, protocol=-1)

            with open(self.pers_keystone + '/tenants.pickle', 'wb') as f:
                pickle.dump(tenants, f, protocol=-1)

            with open(self.pers_keystone + '/tenants_by_name.pickle', 'wb') as\
                    f:
                pickle.dump(tenants_by_name, f)

            with open(self.pers_keystone + '/asignments.pickle', 'wb') as f:
                pickle.dump(roles_a, f, protocol=-1)

            with open(self.pers_keystone + '/roles_by_user.pickle', 'wb') as f:
                pickle.dump(roles_by_user, f, protocol=-1)

            with open(self.pers_keystone + '/roles_by_project.pickle', 'wb') as\
                    f:
                pickle.dump(roles_by_project, f, protocol=-1)

        self.roles = self._convert(roles)
        self.users = self._convert(users)
        self.users_by_name = self._convert(users_by_name)
        self.tenants = self._convert(tenants)
        self.tenants_by_name = self._convert(tenants_by_name)
        self.roles_a = self._convert(roles_a)


    def _get_nova_data(self):
        """ get data from nova"""
        dict_object = self.objects_strategy != OpenStackMap.DIRECT_OBJECTS
        save = dict_object and \
            self.objects_strategy != OpenStackMap.NO_CACHE_OBJECTS

        nova = self.osclients.get_novaclient()
        vms = nova.servers.list(search_opts={'all_tenants': 1})

        if dict_object:
            vms = dict((vm.id, vm.to_dict()) for vm in vms)
        else:
            self.vms = dict((vm.id, vm) for vm in vms)
            return

        if save:
            with open(self.pers_region + '/vms.pickle', 'wb') as f:
                pickle.dump(vms, f, protocol=-1)

        self.vms = self._convert(vms)

    def _get_cinder_data(self):
        """get data from cinder"""
        dict_object = self.objects_strategy != OpenStackMap.DIRECT_OBJECTS
        save = dict_object and \
            self.objects_strategy != OpenStackMap.NO_CACHE_OBJECTS

        cinder = self.osclients.get_cinderclient()
        volumes = cinder.volumes.list(search_opts={'all_tenants': 1})
        snapshots = cinder.volume_snapshots.list(
            search_opts={'all_tenants': 1})
        backups = cinder.backups.list(search_opts={'all_tenants': 1})

        if dict_object:
            volumes = dict((volume.id, volume.__dict__) for volume in volumes)
            snapshots = dict((snapshot.id, snapshot.__dict__) for snapshot in
                             snapshots)
            backups = dict((backup.id, backup.__dict__) for backup in backups)
        else:
            self.volumes = dict((volume.id, volume) for volume in volumes)
            self.volume_snapshots = dict((snapshot.id, snapshot) for snapshot
                                         in snapshots)
            self.volume_backups = dict((backup.id, backup) for backup in
                                       backups)
            return

        if save:
            with open(self.pers_region + '/volumes.pickle', 'wb') as f:
                pickle.dump(volumes, f, protocol=-1)
            with open(self.pers_region + '/volume_snapshots.pickle', 'wb') as \
                    f:
                pickle.dump(snapshots, f, protocol=-1)
            with open(self.pers_region + '/volume_backups.pickle', 'wb') as f:
                pickle.dump(backups, f, protocol=-1)

        self.volumes = self._convert(volumes)
        self.volume_snapshots = self._convert(snapshots)
        self.volume_backups = self._convert(backups)

    def _get_glance_data(self):
        """get data from glance"""
        dict_object = self.objects_strategy != OpenStackMap.DIRECT_OBJECTS
        save = dict_object and \
            self.objects_strategy != OpenStackMap.NO_CACHE_OBJECTS

        glance = self.osclients.get_glanceclient()
        images = glance.images.findall()

        if dict_object:
            images = dict((image.id, image.to_dict()) for image in
                          glance.images.findall())
        else:
            self.images = dict((image.id, image) for image in images)
            return

        if save:
            with open(self.pers_region + '/images.pickle', 'wb') as f:
                pickle.dump(images, f, protocol=-1)

        self.images = self._convert(images)

    def _get_neutron_data(self):
        """get network data from neutron"""
        dict_object = self.objects_strategy != OpenStackMap.DIRECT_OBJECTS
        save = dict_object and \
            self.objects_strategy != OpenStackMap.NO_CACHE_OBJECTS

        neutron = self.osclients.get_neutronclient()
        networks = neutron.list_networks()['networks']
        subnets = neutron.list_subnets()['subnets']
        routers = neutron.list_routers()['routers']
        sec_grps = neutron.list_security_groups()['security_groups']
        floatingips = neutron.list_floatingips()['floatingips']
        ports = neutron.list_ports()['ports']

        nets = dict((network['id'], network) for network in networks)
        snets = dict((subnet['id'], subnet) for subnet in subnets)
        routers = dict((router['id'], router) for router in routers)
        floatingips = dict((floatingip['id'], floatingip) for floatingip in
                               floatingips)
        sec_grps = dict((sg['id'], sg) for sg in sec_grps)
        ports = dict((port['id'], port) for port in ports)

        if dict_object:
            # neutron objects are already dicts, so they do not need conversion
            pass
        else:
            self.networks = nets
            self.subnets = snets
            self.routers = routers
            self.floatingips = floatingips
            self.security_groups = sec_grps
            self.ports = ports
            return

        if save:
            with open(self.pers_region + '/networks.pickle', 'wb') as f:
                pickle.dump(nets, f, protocol=-1)

            with open(self.pers_region + '/subnetworks.pickle', 'wb') as f:
                pickle.dump(snets, f, protocol=-1)

            with open(self.pers_region + '/routers.pickle', 'wb') as f:
                pickle.dump(routers, f, protocol=-1)

            with open(self.pers_region + '/floatingips.pickle', 'wb') as f:
                pickle.dump(floatingips, f, protocol=-1)

            with open(self.pers_region + '/securitygroups.pickle', 'wb') as f:
                pickle.dump(sec_grps, f, protocol=-1)

            with open(self.pers_region + '/ports.pickle', 'wb') as f:
                pickle.dump(ports, f, protocol=-1)

        self.networks = self._convert(nets)
        self.subnets = self._convert(snets)
        self.routers = self._convert(routers)
        self.floatingips = self._convert(floatingips)
        self.security_groups = self._convert(sec_grps)
        self.ports = self._convert(ports)

    def load_nova(self):
        """load nova data: vms"""
        if self.objects_strategy == OpenStackMap.USE_CACHE_OBJECTS and \
                os.path.exists(self.pers_region + '/vms.pickle'):
            self.vms = self._load('vms')
        else:
            self._get_nova_data()


    def load_glance(self):
        """load glance data: images"""
        if self.objects_strategy == OpenStackMap.USE_CACHE_OBJECTS and \
                os.path.exists(self.pers_region + '/images.pickle'):
            self.images = self._load('images')
        else:
            self._get_glance_data()

    def load_neutron(self):
        """load neutron (network) data: networks, subnets, routers,
           floatingips, security_groups, ports"""
        if self.objects_strategy == OpenStackMap.USE_CACHE_OBJECTS and \
                os.path.exists(self.pers_region + '/networks.pickle'):
            self.networks = self._load('networks')
            self.subnets = self._load('subnetworks')
            self.routers = self._load('routers')
            self.floatingips = self._load('floatingips')
            self.security_groups = self._load('securitygroups')
            self.ports = self._load('ports')
        else:
            self._get_neutron_data()

    def load_keystone(self):
        """load keystone data: users, tenants, roles, roles_a,
           users_by_name, tenants_by_name, roles_by_project, roles_by_user
        """
        if self.objects_strategy == OpenStackMap.USE_CACHE_OBJECTS and \
                os.path.exists(self.pers_keystone + '/users.pickle'):
            self.users = self._load_fkeystone('users')
            self.users_by_name = self._load_fkeystone('users_by_name')
            self.tenants = self._load_fkeystone('tenants')
            self.tenants_by_name = self._load_fkeystone('tenants_by_name')
            self.roles_a = self._load_fkeystone('asignments')
            self.roles = self._load_fkeystone('roles')
            self.roles_by_project = self._load_fkeystone('roles_by_project')
            self.roles_by_user = self._load_fkeystone('roles_by_user')
        else:
            self._get_keystone_data()

    def load_cinder(self):
        """load cinder data: volumes, volume_backups, volume_snapshots
        """
        if self.objects_strategy == OpenStackMap.USE_CACHE_OBJECTS and \
                os.path.exists(self.pers_region + '/volumes.pickle'):
            self.volumes = self._load('volumes')
            self.volume_backups = self._load('volume_backups')
            self.volume_snapshots = self._load('volume_snapshots')
        else:
            self._get_cinder_data()

    def load_all(self):
        """load all data"""
        self.load_nova()
        self.load_neutron()
        self.load_glance()
        self.load_cinder()
        self.load_keystone()

    def change_region(self, region):
        """change region and invoke load_all"""
        self.pers_region = self.persistence_dir + '/' + region
        if not os.path.exists(self.pers_region) and self.objects_strategy\
           not in (OpenStackMap.DIRECT_OBJECTS, OpenStackMap.NO_CACHE_OBJECTS):
            os.mkdir(self.pers_region)
        self.osclients.set_region(region)
        self.load_all()
