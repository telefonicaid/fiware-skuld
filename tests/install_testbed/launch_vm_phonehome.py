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
import launch_vm


# Get networks
def deploy_phone_home_vm():
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
    floating_ip = launch_vm.obtain_floating_ips(1, 1)[0]

    launch_vm.create_key_pair()

    sg_name = "phonehome"
    vm_name = "phonehome"
    ports = [8081]
    launch_vm.deploy_security_groups(sg_name, ports)

    if settings.multinetwork:
        security_group_id = nova.security_groups.find(name=sg_name).id
        port = launch_vm.create_port_multi_ip(security_group_id)
        nics = [{'net-id': network['management']},
                {'net-id': network['tunnel']},
                {'port-id': port['port']['id']}]
    else:
        nics = [{'net-id': network['management']}]

    keystone_ip = floating_ip

    init_script = os.path.join(os.path.split(sys.argv[0])[0], settings.init_script_phone_home)
    server = launch_vm.launch_vm(vm_name, settings.flavor_name_phone_home, sg_name,
                       settings.image_phone_home, nics, init_script, keystone_ip, '', '')
    print "Keystone IP {0}".format(keystone_ip)

    # assign the floating ip
    if floating_ip:
        print('Assigning floating IP ' + floating_ip)
        server.add_floating_ip(floating_ip)


if __name__ == "__main__":
    deploy_phone_home_vm()
