#!/usr/bin/env python
# -*- encoding: utf-8 -*-
##
# Copyright 2018 FIWARE Foundation, e.V.
# All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
##


__author__ = "Jose Ignacio Carretero Guarde"


import json
import sys
from functions import *
from OpenstackQueries import OpenstackQueries
from collections import Counter


if __name__ == "__main__":
    q = OpenstackQueries('fiware-users.ini')
    token = q.token
    sys.stderr.write(q.token + "\n")

    d={}

    endpoint_groups = q.get_all_endpoint_groups(token=token)
    d['endpoint_groups'] = endpoint_groups

    project_list = q.get_all_projects(token=token)
    d['projects']=project_list

    user_list = q.get_all_users(token=token)
    d['users']=user_list

    role_list = q.get_role_list(token=token)
    d['roles']=role_list

    role_assignment_list = q.get_role_assignment_list(token=token)
    d['role_assignments']=role_assignment_list

    q.get_all_endpoint_groups_projects(token, endpoint_groups)

    servers = q.get_all_servers(token)
    d['servers'] = servers

    routers = q.get_all_routers(token)
    d['routers'] = routers

    networks = q.get_all_networks(token)
    d['networks'] = networks

    images = q.get_all_images(token)
    d['images'] = images

    ports = q.get_all_ports(token)
    d['ports'] = ports

    cinder_volumes = q.get_all_volumes(token=token)
    d['volumes'] = cinder_volumes

    ## Print how many users there are for every role
    role_assingments_count = Counter([k['role_id'] for k in d['role_assignments'] if k.get('role_id')])

    d['sum_up'] = {'users': len(d['users']), 'projects': len(d['projects']), 
                   'role_assignments_count': role_assingments_count}

    sys.stdout.write(json.dumps(d))
    sys.stdout.flush()
