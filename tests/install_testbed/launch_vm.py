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
import sys

from utils.osclients import osclients

network_names = {
   'management': 'node-int-net-01',
   'tunnel': 'tunnel-net',
   'external': 'external-net'
}

subnet = {
   'management': '192.168.192.0/18',
   'tunnel': '192.168.57.0/24',
   'external': '192.168.58.0/24'
}

key_name = 'createimage'
security_group = 'sshopen'
# Use this IP if it is available.
preferred_ip = None


# Testbed image
flavor_name = 'm1.large'
image_name = 'keyrock-R4.4'
vm_name = 'testbedskuld'
# filename of init_script
init_script = 'cloudconfig'

# Test image
flavor_name_test = 'm1.tiny'
image_name_test = 'base_debian_7'
vm_name_test = 'testvm'

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
    if init_script:
        data = open(init_script).read()
        extra_params['userdata'] = data

    server =  nova_c.servers.create(
        vm_n, flavor=flavor.id, image=image_id, key_name=key_name,
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

def create_port_multi_ip():
    """Create port in external network, with 5 IPs (this is the maximum allowed
    with the default neutron configuration).

    Be aware that this port is not deleted when the VM is deleted!

    Another point is that security group may be different than the security
    group of the VM.

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

    return neutron.create_port(
        {'port': {'network_id': network['external'], 'fixed_ips': fixed_ips}})


# Get networks

network = dict()
neutron = osclients.get_neutronclient()
for net in neutron.list_networks()['networks']:
    for n in network_names:
        if net['name'] == network_names[n]:
            network[n] = net['id']

for n in network_names:
    if not n in network:
        network[n] = neutron.create_network({'network': {'name':
            network_names[n], 'admin_state_up': True}})['network']['id']
        # create subnetwork. It is not possible to assign a network
        # to a VM without a subnetwork.
        neutron.create_subnet({'subnet': {'network_id': network[n],
            'ip_version': 4, 'cidr': subnet[n]}})

# Get a floating IP
floating_ip = None
for ip in neutron.list_floatingips()['floatingips']:
    floating_ip = ip['floating_ip_address']
    if not preferred_ip or preferred_ip == floating_ip:
        break

# Launch testbed VM
nics = [{'net-id': network['management']},
        {'net-id': network['tunnel']},
        {'net-id': network['external']}]
# change with this to use pre-allocated port
#        {'port-id': port['port']['id']}]
server = launch_vm(vm_name, flavor_name, security_group, image_name, nics,
                   init_script)

# assign the floating ip
if floating_ip:
    print('Assigning floating IP ' + floating_ip)
    server.add_floating_ip(floating_ip)

# Launch test VM
nics = [{'net-id': network['management']},
        {'net-id': network['external']}]

server = launch_vm(vm_name_test, flavor_name_test, security_group,
                   image_name_test, nics)
