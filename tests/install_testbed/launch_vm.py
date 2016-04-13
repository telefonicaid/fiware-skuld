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
from os import environ as env
from fiwareskuld.utils.osclients import osclients
import settings


def launch_vm(vm_n, flavor_n, securityg_n, image_n, ifaces, user_data=None, keystone_ip=None,
              region=None, region_keystone=None):
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

    extra_params['meta'] = {"Region": region, "keystone_ip": keystone_ip, "region_keystone": region_keystone}

    server = nova_c.servers.create(
        vm_n, flavor=flavor.id, image=image_id, key_name=settings.key_name,
        security_groups=[securityg_n], nics=ifaces, **extra_params)

    print('{0}: VM with UUID {1}'.format(region, server.id))

    # wait until the vm is active
    tries = 1
    while server.status != 'ACTIVE' and tries < 30:
        print('Waiting for ACTIVE status. (Try ' + str(tries) + '/30)')
        time.sleep(5)
        try:
            server = nova_c.servers.get(server.id)
        except:
            pass
        tries += 1

    if server.status != 'ACTIVE':
        sys.stderr.write('Failed waiting the VM is active\n')
        sys.exit(-1)

    return server


def deploy_security_groups(sg_name):
    # Create security group if it does not exist
    nova = osclients.get_novaclient()
    neutron = osclients.get_neutronclient()
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
        nova.security_group_rules.create(
            g.id, ip_protocol='tcp', from_port=35357, to_port=35357, cidr=settings.ingress_ssh_ip_range)

        # This type of rule requires the neutron API

        neutron.create_security_group_rule(
            {'security_group_rule': {'direction': 'ingress', 'security_group_id': g.id,
                                     'remote_group_id': g.id}})


def create_key_pair():
    nova = osclients.get_novaclient()
    keys = nova.keypairs.findall(name=settings.key_name)
    if not keys:
        new_key = nova.keypairs.create(settings.key_name)
        filename = os.path.expanduser('~/.ssh/' + settings.key_name)
        with open(filename, 'w') as f:
            f.write(new_key.private_key)
        # make the file only readable by the owner
        os.chmod(filename, 0600)


def obtain_floating_ips(num_floating_ips, booked_ips_num):
    neutron = osclients.get_neutronclient()
    nova = osclients.get_novaclient()

    # Get a floating IP
    booked_ips = []
    if booked_ips_num == 1:
        if "BOOKED_IP" in env:
            booked_ips.append(env["BOOKED_IP"])
    elif booked_ips_num == 2:
        if "BOOKED_IP1" in env:
            booked_ips.append(env["BOOKED_IP1"])
        if "BOOKED_IP2" in env:
            booked_ips.append(env["BOOKED_IP2"])

    floating_ips = []
    available_floating_ips = []

    for ip in neutron.list_floatingips()['floatingips']:
        if not ip["fixed_ip_address"]:
            available_floating_ips.append(ip["floating_ip_address"])

    print booked_ips
    if booked_ips:
        for booked_ip in booked_ips:
            print booked_ip
            print available_floating_ips
            if booked_ip in available_floating_ips:
                floating_ips.append(booked_ip)
            else:
                print 'ERROR. The booked ip {0} is not available'.format(booked_ip)
                exit()


    for ip in available_floating_ips:
        if ip not in floating_ips:
            floating_ips.append(ip)
        if len(floating_ips) == num_floating_ips:
            break

    while len(floating_ips) < num_floating_ips:
        # allocate floating ip if it does not exist
        new_floating_ip = nova.floating_ips.create('public-ext-net-01').ip
        floating_ips.append(new_floating_ip)

    return floating_ips


def create_port_multi_ip(security_group_id=None):
    """Create port in external network, with 5 IPs (this is the maximum allowed
    with the default neutron configuration).

    Be aware that this port is not deleted when the VM is deleted!

    Another point is that security group may be different than the security
    group of the VM.

    :param security_group_id: The security group
    :return: a pre-allocated port
    """
    neutron = osclients.get_neutronclient()
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


def prepare_networks():
    network = dict()
    neutron = osclients.get_neutronclient()
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
    return network


# Get networks
def deploy_testbed():
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
    floating_ip = obtain_floating_ips(1, 1)[0]

    create_key_pair()

    sg_name = sg_name = settings.security_group
    deploy_security_groups(sg_name)

    if settings.multinetwork:
        security_group_id = nova.security_groups.find(name=sg_name).id
        port = create_port_multi_ip(security_group_id)
        nics = [{'net-id': network['management']},
                {'net-id': network['tunnel']},
                {'port-id': port['port']['id']}]
    else:
        nics = [{'net-id': network['management']}]

    keystone_ip = floating_ip
    if env["Region1"]:
        region = env["Region1"]
    else:
        region = 'RegionOne'

    region_keystone = region
    init_script = os.path.join(os.path.split(sys.argv[0])[0], settings.init_script)
    server = launch_vm(settings.vm_name, settings.flavor_name, sg_name,
                       settings.image_name, nics, init_script, keystone_ip, region,
                       region_keystone)
    print "Keystone IP {0}".format(keystone_ip)
    print "Region1 IP: {0} {1}".format(region, keystone_ip)
    # assign the floating ip
    if floating_ip:
        print('Assigning floating IP ' + floating_ip)
        server.add_floating_ip(floating_ip)

    if settings.multinetwork:
        # Launch test VM
        nics = [{'net-id': network['management']},
                {'net-id': network['external']}]
        launch_vm(settings.vm_name_test, settings.flavor_name_test, sg_name,
                  settings.image_name_test, nics, init_script, keystone_ip, region,
                  region_keystone)

if __name__ == "__main__":
    deploy_testbed()
