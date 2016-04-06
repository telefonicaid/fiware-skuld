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


import os
import os.path
import time
from fiwareskuld.utils.osclients import osclients
import settings


# Get networks
def destroy_testbeds():
    """
    It delete all the testbed deployed automatically
    :return: nothing()
    """
    nova = osclients.get_novaclient()

    # Delete vms
    servers = nova.servers.findall()
    for server in servers:
        if server.name == settings.vm_name:
            print "Deleting VM " + server.id
            nova.servers.delete(server)
            while nova.servers.find(server):
                time.sleep(2)

    # Delete keypair
    keys = nova.keypairs.findall(name=settings.key_name)
    for key in keys:
        print "Deleting keypair " + key.name
        nova.keypairs.delete(key)
        filename = os.path.expanduser('~/.ssh/' + settings.key_name)
        os.remove(filename)

    # Delete securing groups
    sg_name = settings.security_group
    sec_groups = nova.security_groups.findall(name=sg_name)
    for sec in sec_groups:
        print "Deleting sec group " + sec.name
        nova.security_groups.delete(sec)

if __name__ == "__main__":
    destroy_testbeds()
