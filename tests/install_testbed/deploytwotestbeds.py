#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#
# Copyright 2016 Telefónica Investigación y Desarrollo, S.A.U
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

import time
import sys
import os
import os.path

from fiwareskuld.utils.osclients import osclients
import settings
import launch_vm


# Get networks
def deploy_testbeds():
    network = dict()
    neutron = osclients.get_neutronclient()
    nova = osclients.get_novaclient()

    for net in neutron.list_networks()['networks']:
        for n in settings.network_names:
            if net['name'] == settings.network_names[n]:
                network[n] = net['id']

    for n in settings.network_names:
        if n not in network:
            if n == 'management':
                sys.stderr.write('Fatal error: network ' + settings.network_names[n] +
                                 'not found.\n')
                sys.exit(-1)

            network[n] = neutron.create_network(
                {'network': {'name': settings.network_names[n], 'admin_state_up': True}})['network']['id']
            # create subnetwork. It is not possible to assign a network
            # to a VM without a subnetwork.
            neutron.create_subnet({'subnet': {'network_id': network[n], 'ip_version': 4, 'cidr': settings.subnet[n],
                                              'gateway_ip': None}})

    # Get a floating IP
    print 'ips'
    floating_ip = []
    for ip in neutron.list_floatingips()['floatingips']:
        floating_ip.append(ip['floating_ip_address'])
        print ip['floating_ip_address']
        if len(floating_ip) == 2:
            break

    while len(floating_ip) < 2:
        # allocate floating ip if it does not exist
        floating_ip = nova.floating_ips.create('public-ext-net-01').ip

    keys = nova.keypairs.findall(name=settings.key_name)
    if not keys:
        new_key = nova.keypairs.create(settings.key_name)
        filename = os.path.expanduser('~/.ssh/' + settings.key_name)
        with open(filename, 'w') as f:
            f.write(new_key.private_key)
        # make the file only readable by the owner
        os.chmod(filename, 0600)

    # Create security group if it does not exist
    sg_name = settings.security_group
    sec_groups = nova.security_groups.findall(name=sg_name)
    if not sec_groups:
        g = nova.security_groups.create(name=sg_name, description=sg_name)
        # Open
        nova.security_group_rules.create(
            g.id, ip_protocol='icmp', from_port=-1, to_port=-1, cidr=settings.ingress_icmp_ip_range)
        # Open SSH (port TCP 22)
        nova.security_group_rules.create(
            g.id, ip_protocol='tcp', from_port=22, to_port=22, cidr=settings.ingress_ssh_ip_range)
        nova.security_group_rules.create(
            g.id, ip_protocol='tcp', from_port=5000, to_port=5000, cidr=settings.ingress_ssh_ip_range)
        nova.security_group_rules.create(
            g.id, ip_protocol='tcp', from_port=8774, to_port=8776, cidr=settings.ingress_ssh_ip_range)
        nova.security_group_rules.create(
            g.id, ip_protocol='tcp', from_port=9696, to_port=9696, cidr=settings.ingress_ssh_ip_range)
        nova.security_group_rules.create(
            g.id, ip_protocol='tcp', from_port=8080, to_port=8080, cidr=settings.ingress_ssh_ip_range)
        nova.security_group_rules.create(
            g.id, ip_protocol='tcp', from_port=9292, to_port=9292, cidr=settings.ingress_ssh_ip_range)
        # This type of rule requires the neutron API

        neutron.create_security_group_rule(
            {'security_group_rule': {'direction': 'ingress', 'security_group_id': g.id,
                                     'remote_group_id': g.id}})

    # Launch testbed VM
    if settings.multinetwork:
        security_group_id = nova.security_groups.find(name=sg_name).id
        port = launch_vm.create_port_multi_ip(security_group_id)
        nics = [{'net-id': network['management']},
                {'net-id': network['tunnel']},
                {'port-id': port['port']['id']}]
    else:
        nics = [{'net-id': network['management']}]

    print 'RegionOne'
    keystone_ip = floating_ip[0]
    region = 'RegionOne'
    region_keystone = 'RegionOne'
    init_script = os.path.join(os.path.split(sys.argv[0])[0], settings.init_script)
    server = launch_vm.launch_vm(settings.vm_name, settings.flavor_name, sg_name,
                                 settings.image_name, nics, init_script, keystone_ip, region,
                                 region_keystone)

    # assign the floating ip
    if floating_ip:
        print('Assigning floating IP ' + floating_ip[0])
        server.add_floating_ip(floating_ip[0])

    if settings.multinetwork:
        # Launch test VM
        nics = [{'net-id': network['management']},
                {'net-id': network['external']}]
        launch_vm.launch_vm(settings.vm_name_test, settings.flavor_name_test, sg_name,
                            settings.image_name_test, nics, init_script, keystone_ip, region,
                            region_keystone)

    time.sleep(120)
    print 'RegionTwo'
    region = 'RegionTwo'
    init_script = os.path.join(os.path.split(sys.argv[0])[0], settings.init_script)
    server = launch_vm.launch_vm(settings.vm_name, settings.flavor_name, sg_name,
                                 settings.image_name, nics, init_script, keystone_ip, region,
                                 region_keystone)

    # assign the floating ip
    if floating_ip:
        print('Assigning floating IP ' + floating_ip[1])
        server.add_floating_ip(floating_ip[1])

    if settings.multinetwork:
        # Launch test VM
        nics = [{'net-id': network['management']},
                {'net-id': network['external']}]
        launch_vm.launch_vm(settings.vm_name_test, settings.flavor_name_test, sg_name,
                            settings.image_name_test, nics, init_script, keystone_ip, region,
                            region_keystone)

if __name__ == "__main__":
    deploy_testbeds()
