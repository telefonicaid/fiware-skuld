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
def deploy_three_glances():

    nova = osclients.get_novaclient()

    network = launch_vm.prepare_networks()

    floating_ips = launch_vm.obtain_floating_ips(3, 2)

    launch_vm.create_key_pair()
    sg_name = settings.security_group

    launch_vm.deploy_security_groups(sg_name)

    # Launch testbed VM
    if settings.multinetwork:
        security_group_id = nova.security_groups.find(name=sg_name).id
        port = launch_vm.create_port_multi_ip(security_group_id)
        nics = [{'net-id': network['management']},
                {'net-id': network['tunnel']},
                {'port-id': port['port']['id']}]
    else:
        nics = [{'net-id': network['management']}]

    keystone_ip = floating_ips[0]
    if "Region1" in env:
        region = env["Region1"]
    else:
        region = 'RegionOne'
    print region
    print "Keystone IP {0}".format(keystone_ip)
    print "Region1 IP: {0} {1}".format(region, keystone_ip)

    region_keystone = region
    deploy_glance(nics, keystone_ip, region, region_keystone, floating_ips[0], network)

    time.sleep(120)
    if "Region2" in env:
        region = env["Region2"]
    else:
        region = 'RegionTwo'

    print region
    print "Region2 IP: {0} {1}".format(region, floating_ips[2])
    deploy_glance(nics, keystone_ip, region, region_keystone, floating_ips[2], network)

    if "Region3" in env:
        region = env["Region3"]
    else:
        region = 'RegionThree'

    print region
    region_keystone = region
    keystone_ip = floating_ips[1]
    print "Region3 IP: {0} {1}".format(region, floating_ips[1])
    deploy_glance(nics, keystone_ip, region, region_keystone, floating_ips[1], network)


def deploy_glance(nics, keystone_ip, region, region_keystone, floating_ip, network):
    sg_name = settings.security_group
    init_script = os.path.join(os.path.split(sys.argv[0])[0], settings.init_script_only_glance)
    server = launch_vm.launch_vm(settings.vm_name, settings.flavor_name, sg_name,
                                 settings.image_name, nics, init_script, keystone_ip, region,
                                 region_keystone)

    # assign the floating ip
    if floating_ip:
        print('Assigning floating IP ' + floating_ip)
        server.add_floating_ip(floating_ip)

    if settings.multinetwork:
        # Launch test VM
        nics = [{'net-id': network['management']},
                {'net-id': network['external']}]
        launch_vm.launch_vm(settings.vm_name_test, settings.flavor_name_test, sg_name,
                            settings.image_name_test, nics, init_script, keystone_ip, region,
                            region_keystone)


if __name__ == "__main__":
    deploy_three_glances()
