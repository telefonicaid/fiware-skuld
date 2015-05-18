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

novaclient = osclients.get_novaclient()

"""This function is to be used with the admin"""
def get_all_vms():
    tenants = dict()
    for vm in novaclient.servers.list(search_opts={'all_tenants': 1}):
        if vm.tenant_id not in tenants:
            tenants[vm.tenant_id] = list()
        tenants[vm.tenat_id].append((vm.id, vm.user_id))
    return tenants

def get_tenant_vms(tenant_id=None):
    vms = list()
    if not tenant_id:
        tenant_id = osclients.get_session().get_project_id()

    for vm in novaclient.servers.list():
        vms.append((vm.id, vm.user_id))
    return vms

def delete_tenant_vms(tenant_id=None):
    if not tenant_id:
        tenant_id = osclients.get_session().get_project_id()

    for vm in novaclient.servers.list():
        vm.delete()

"""Only is possible to obtain the keypairs of the user"""
def get_user_keypairs(tenant_id=None):
    keypairs = list()
    if not tenant_id:
        tenant_id = osclients.get_session().get_project_id()

    for keypair in novaclient.keypairs.list():
        keypairs.append(keypair.id)
    return keypairs

def delete_user_keypairs(tenant_id=None):
    if not tenant_id:
        tenant_id = osclients.get_session().get_project_id()

    for keypair in novaclient.keypairs.list():
        keypair.delete()

"""Only is possible to obtain the security groups of the tenant"""
def get_tenant_security_groups(tenant_id=None):
    security_groups = list()
    if not tenant_id:
        tenant_id = osclients.get_session().get_project_id()

    for secgroup in novaclient.security_groups.list():
        #print secgroup.tenant_id, secgroup.id
        if secgroup.name == 'default':
            continue
        security_groups.append(secgroup.id)
    return security_groups

def delete_tenant_security_groups(tenant_id=None):
    if not tenant_id:
        tenant_id = osclients.get_session().get_project_id()

    for secgroup in novaclient.security_groups.findall():
        if secgroup.name == 'default':
            continue
        secgroup.delete()


