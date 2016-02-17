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
__author__ = 'chema'

import time
import sys
import os
import os.path

from utils.osclients import osclients
import settings


def launch_vm(vm_n, flavor_n, securityg_n, image_n, ifaces, user_data=None):
    """ Launch a VM and wait until it is ready.

    :param vm_n: virtual machine name
    :param flavor_n: flavor name
    :param securityg_n: securigy group name
    :param image_n: image name
    :param ifaces: array with the interfaces
    :param user_data: optional init script or cloud init data
    :return: a VM object
    """
    # Get image
    image_id = osclients.get_glanceclient().images.find(name=image_n).id

    nova_c = osclients.get_novaclient()
    flavor = nova_c.flavors.find(name=flavor_n)

    extra_params = dict()

    # load script to launch with nova.servers.create()
    if user_data:
        data = open(user_data).read()
        extra_params['userdata'] = data

    server = nova_c.servers.create(
        vm_n, flavor=flavor.id, image=image_id, key_name=settings.key_name,
        security_groups=[securityg_n], nics=ifaces, **extra_params)

    print('Created VM with UUID ' + server.id)

    # wait until the vm is active
    tries = 1
    while server.status != 'ACTIVE' and tries < 30:
        print('Waiting for ACTIVE status. (Try ' + str(tries) + '/30)')
        time.sleep(5)
        server = nova_c.servers.get(server.id)
        tries += 1

    if server.status != 'ACTIVE':
        sys.stderr.write('Failed waiting the VM is active\n')
        sys.exit(-1)

    return server


def create_port_multi_ip(security_group_id=None):
    """Create port in external network, with 5 IPs (this is the maximum allowed
    with the default neutron configuration).

    Be aware that this port is not deleted when the VM is deleted!

    Another point is that security group may be different than the security
    group of the VM.

    :param security_group_id: The security group
    :return: a pre-allocated port
    """

    subnet_external = None
    for subnet in neutron.list_subnets()['subnets']:
        if subnet['network_id'] == network['external']:
            subnet_external = subnet['id']

    fixed_ips = list()
    for i in range(200, 205):
        fixed_ip = dict()
        fixed_ip['subnet_id'] = subnet_external
        fixed_ip['ip_address'] = '192.168.58.%d' % i
        fixed_ips.append(fixed_ip)

    p = {'port': {'network_id': network['external'], 'fixed_ips': fixed_ips}}
    if security_group_id:
        p['port']['security_groups'] = [security_group_id]
    return neutron.create_port(p)

# Get networks

network = dict()
neutron = osclients.get_neutronclient()
nova = osclients.get_novaclient()

for net in neutron.list_networks()['networks']:
    for n in settings.network_names:
        if net['name'] == settings.network_names[n]:
            network[n] = net['id']

for n in settings.network_names:
    if not n in network:
        if n == 'management':
            sys.stderr.write('Fatal error: network ' + settings.network_names[n] +
                             'not found.\n')
            sys.exit(-1)

        network[n] = neutron.create_network(
            {'network': {'name': settings.network_names[n], 'admin_state_up': True}})['network']['id']
        # create subnetwork. It is not possible to assign a network
        # to a VM without a subnetwork.
        neutron.create_subnet({'subnet': {'network_id': network[n],
            'ip_version': 4, 'cidr': settings.subnet[n], 'gateway_ip': None}})

# Get a floating IP
floating_ip = None
for ip in neutron.list_floatingips()['floatingips']:
    floating_ip = ip['floating_ip_address']
    if not settings.preferred_ip or settings.preferred_ip == floating_ip:
        break

if not floating_ip:
    # allocate floating ip if it does not exist
    floating_ip = nova.floating_ips.create('ext-net').ip

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
    # This type of rule requires the neutron API
    neutron.create_security_group_rule(
        {'security_group_rule': {'direction': 'ingress', 'security_group_id': g.id,
                                 'remote_group_id': g.id}})

# Launch testbed VM
if settings.multinetwork:
    security_group_id = nova.security_groups.find(name=sg_name).id
    port = create_port_multi_ip(security_group_id)
    nics = [{'net-id': network['management']},
            {'net-id': network['tunnel']},
            {'port-id': port['port']['id']}]
else:
    nics = [{'net-id': network['management']}]

init_script = os.path.join(os.path.split(sys.argv[0])[0], settings.init_script)
server = launch_vm(settings.vm_name, settings.flavor_name, sg_name,
                   settings.image_name, nics, init_script)

# assign the floating ip
if floating_ip:
    print('Assigning floating IP ' + floating_ip)
    server.add_floating_ip(floating_ip)

if settings.multinetwork:
    # Launch test VM
    nics = [{'net-id': network['management']},
            {'net-id': network['external']}]

    launch_vm(settings.vm_name_test, settings.flavor_name_test, sg_name,
              settings.image_name_test, nics, init_script)
