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

import osclients

neutron = osclients.get_neutronclient()
cinder = osclients.get_cinderclient()
glance = osclients.get_glanceclient()
nova = osclients.get_novaclient()

volume = cinder.volumes.create(name='cindervolume', size=1)

external_net=None
for net in neutron.list_networks()['networks']:
    if net['router:external']:
        external_net = net['id']
        break

image = glance.images.create(
    container_format='bare', name='testimage1', disk_format='qcow2',
    data='aaaaa')

keypair = nova.keypairs.create(name='testpublickey')
secgroup = nova.security_groups.create('testsecgroup',
                                       'a security group for testing')
floatingip = nova.floating_ips.create(pool=external_net)

router = neutron.create_router(
    {'router': {'name': 'testrouter', 'admin_state_up': True}})['router']
network = neutron.create_network(
    {'network': {'name': 'testnetwork', 'admin_state_up': True, }})['network']


subnet = neutron.create_subnet(
    {'subnet': {'name': 'testsubnet', 'network_id': network['id'],
    'ip_version': 4, 'cidr': '192.168.1.0/24',
    'dns_nameservers': ['8.8.8.8']}})['subnet']

neutron.add_interface_router(router['id'], {'subnet_id': subnet['id']})
neutron.add_gateway_router(router['id'], {'network_id': external_net})

# The volume must be available before creating the snapshot.
snapshot = cinder.volume_snapshots.create(volume.id)
