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
import cPickle as pickle
import sys


def get_and_save():
    keystone = osclients.get_keystoneclientv3()
    with open('persistence/roles.pickle', 'wb') as f:
        roles = list(role.to_dict() for role in keystone.roles.list())
        pickle.dump(roles, f, protocol=-1)

    with open('persistence/users.pickle', 'wb') as f:
        users = list(user.to_dict() for user in keystone.users.list())
        pickle.dump(users, f, protocol=-1)

    with open('persistence/tenants.pickle', 'wb') as f:
        tenants = list(tenant.to_dict() for tenant in keystone.projects.list())
        pickle.dump(tenants, f, protocol=-1)

    with open('persistence/asignments.pickle', 'wb') as f:
        as = list(asig.to_dict() for asig in keystone.role_assignments.list())
        pickle.dump(as, f, protocol=-1)


def get_users_dicts():
    users = pickle.load(open('persistence/users.pickle', 'rb'))
    users_by_email = dict()
    users_by_id = dict()
    for user in users:
        if 'name' in user:
            users_by_email[user['name']] = user
        users_by_id[user['id']] = user
    return (users_by_email, users_by_id)


def get_tenant_dicts():
    tenants = pickle.load(open('persistence/tenants.pickle', 'rb'))
    tenants_by_name = dict()
    tenants_by_id = dict()
    for tenant in tenants:
        tenants_by_id[tenant['id']] = tenant
        tenants_by_name[tenant['name']] = tenant
    return (tenants_by_name, tenants_by_id)


def get_roles_dicts():
    roleasigments = pickle.load(open('persistence/asignments.pickle', 'rb'))
    roles = pickle.load(open('persistence/roles.pickle', 'rb'))
    rolesdict = dict((role['id'], role['name']) for role in roles)
    roles_by_user = dict()
    roles_by_project = dict()
    for roleasig in roleasigments:
        userid = roleasig['user']['id']
        if 'project' in roleasig['scope']:
            projectid = roleasig['scope']['project']['id']
        else:
            projectid = str(roleasig['scope'])
        roleid = roleasig['role']['id']
        if userid not in roles_by_user:
            roles_by_user[userid] = list()
        if projectid not in roles_by_project:
            roles_by_project[projectid] = list()
        roles_by_user[userid].append((rolesdict[roleid], projectid))
        roles_by_project[projectid].append((rolesdict[roleid], userid))
    return (roles_by_user, roles_by_project)
